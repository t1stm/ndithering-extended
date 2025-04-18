import os
import shutil
import subprocess
import sys
from pathlib import Path

from nvibrant import __version__

# Common paths
PACKAGE   = Path(__file__).parent
NVIBRANT  = (PACKAGE.parent)
RESOURCES = (PACKAGE/"resources")
OPEN_GPU  = (NVIBRANT/"open-gpu")
RELEASE   = (NVIBRANT/"release")
BUILD     = (NVIBRANT/"build")

# Common tools
PYTHON = (sys.executable,)
MESON  = (*PYTHON, "-m", "mesonbuild.mesonmain")
NINJA  = (*PYTHON, "-m", "ninja")

# #

def shell(*command: str, echo: bool=True, **kwargs) -> subprocess.CompletedProcess:
    command = tuple(map(str, command))
    if echo: print(f"• Call {command}")
    return subprocess.run(command, **kwargs)

# # Repositories

def get_tags(repo: Path) -> list[str]:
    return list(filter(None,
        subprocess.check_output(("git", "tag"), cwd=repo)
    .decode("utf-8").splitlines()))

def checkout_tag(repo: Path, tag: str) -> subprocess.CompletedProcess:
    return shell("git", "checkout", "-f", tag, cwd=repo)

# # Directories

def mkdir(path: Path) -> Path:
    Path(path).mkdir(parents=True, exist_ok=True)
    return Path(path)

def rmdir(path: Path) -> Path:
    shutil.rmtree(path, ignore_errors=True)
    return Path(path)

def reset_dir(path: Path) -> Path:
    return mkdir(rmdir(path))

# # Drivers

def current_driver() -> str:

    # Safety fallback or override with environment variable
    if (force := os.getenv("NVIDIA_DRIVER_VERSION")):
        return force

    # Seems to be a common and stable path to get the information
    elif (file := Path("/sys/module/nvidia/version")).exists():
        return file.read_text("utf8").strip()

    print("Could not find the current driver version at /sys/module/nvidia/version")
    print("• Run with 'NVIDIA_DRIVER_VERSION=x.y.z nvibrant' to set or force it")
    sys.exit(1)

# ------------------------------------------------------------------------------------------------ #
# Entry points

def actions() -> None:
    for (key, value) in dict(
        GHA_VERSION=__version__,
    ).items():
        print(f"{key}={value}")

def build() -> None:
    mkdir(RESOURCES)

    # Internal structs may differ between versions,
    # compile the project for all nvidia drivers
    for driver in reversed(get_tags(OPEN_GPU)):
        checkout_tag(OPEN_GPU, driver)

        # Configure and compile cpp project
        shell(*MESON, "setup", BUILD,
            "--buildtype", "release",
            "--reconfigure")
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

def main() -> None:
    driver = current_driver()
    nvibrant = RESOURCES / (
        f"nvibrant"
        f"-linux"
        f"-amd64"
        f"-{driver}"
        f"-v{__version__}"
        f".bin"
    )

    if not nvibrant.exists():
        print("Error: No suitable nvibrant binary found on bundled files, tried looking for:")
        print(f"• {nvibrant}")
        print()
        print("Maybe there's a newer version available supporting your driver?")
        print("• GitHub: https://github.com/Tremeschin/nVibrant")
        print("• PyPI: https://pypi.org/project/nvibrant/")
        print("• System update on your package manager")
        sys.exit(1)

    # Ensure is executable and inject incoming argv
    shell("chmod", "+x", nvibrant, echo=False)
    shell(nvibrant, *sys.argv[1:], echo=False)

if __name__ == "__main__":
    main()
