import sys

from nvibrant import (
    RESOURCES,
    __version__,
    current_driver,
    shell,
)


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


if (__name__ == "__main__"):
    main()
