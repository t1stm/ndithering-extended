import sys

from nvibrant import (
    __version__,
    get_best,
    get_driver,
    shell,
)


def main() -> None:
    (version, nvibrant) = get_best()
    current = get_driver()

    # Ensure executable file and pass incoming argv
    call = shell("chmod", "+x", nvibrant, echo=False)
    call = shell(nvibrant, *sys.argv[1:], echo=False)

    if (call.returncode != 0):
        if (version != current):
            print()
            print("-"*80)
            print()
            print(f"Note: This version v{__version__} of nvibrant doesn't bundle exact binaries for your")
            print("      driver (1); the closest previous version (2) was used but failed")
            print()
            print(f"• (1) Current: {current}")
            print(f"• (2) Closest: {version}")
            print()
            print("Maybe there's a newer version available supporting your driver?")
            print("• GitHub: https://github.com/Tremeschin/nVibrant")
            print("• PyPI: https://pypi.org/project/nvibrant/")
            print("• System update on your package manager")
            print()
            print("You can ignore this if the error is about usage and not ioctl.")
        sys.exit(1)

if (__name__ == "__main__"):
    main()
