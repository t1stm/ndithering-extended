#!/usr/bin/env python3
from nvibrant import (
    BUILD,
    MESON,
    NINJA,
    OPEN_GPU,
    RESOURCES,
    __version__,
    checkout_tag,
    get_tags,
    rsdir,
    shell,
)


def build() -> None:
    rsdir(RESOURCES)

    # Configure the project once
    shell(*MESON, "setup", BUILD,
        "--buildtype", "release",
        "--reconfigure")

    # Internal structs may differ between versions,
    # compile the project for all nvidia drivers
    for driver in reversed(get_tags(OPEN_GPU)):
        checkout_tag(OPEN_GPU, driver)
        shell(*NINJA, "-C", BUILD)

        # Name the binary release
        nvibrant = (BUILD/"nvibrant")
        nvibrant.rename(RESOURCES / (
            f"nvibrant"
            f"-linux"
            f"-amd64"
            f"-{driver}"
            f"-v{__version__}"
            f".bin"
        ))

    # Revert back to the main branch
    checkout_tag(OPEN_GPU, "main")

if (__name__ == "__main__"):
    build()
