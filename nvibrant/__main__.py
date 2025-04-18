import shutil
import subprocess
import sys
from pathlib import Path

from nvibrant import __version__

# Common paths
NVIBRANT = Path(__file__).parent.parent
OPEN_GPU = (NVIBRANT/"open-gpu-kernel-modules")
RELEASE  = (NVIBRANT/"release")
BUILD    = (NVIBRANT/"build")

# Common tools
PYTHON = (sys.executable,)
MESON  = (*PYTHON, "-m", "mesonbuild.mesonmain")
NINJA  = (*PYTHON, "-m", "ninja")

def shell(*command: str, **kwargs) -> subprocess.CompletedProcess:
    command = tuple(map(str, command))
    print(f"• Call {command}")
    return subprocess.run(command, **kwargs)

def get_tags(repo: Path) -> list[str]:
    return list(filter(None,
        subprocess.check_output(("git", "tag"), cwd=repo)
    .decode("utf-8").splitlines()))

def checkout_tag(repo: Path, tag: str) -> subprocess.CompletedProcess:
    return shell("git", "checkout", "-f", tag, cwd=repo)

def mkdir(path: Path) -> Path:
    Path(path).mkdir(parents=True, exist_ok=True)
    return Path(path)

def rmdir(path: Path) -> Path:
    shutil.rmtree(path, ignore_errors=True)
    return Path(path)

def reset_dir(path: Path) -> Path:
    return mkdir(rmdir(path))

# ------------------------------------------------------------------------------------------------ #
# Entry points

def build() -> None:
    mkdir(RELEASE)

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
        nvibrant.rename(RELEASE / (
            f"nvibrant"
            f"-linux"
            f"-amd64"
            f"-{driver}"
            f"-v{__version__}"
            f".bin"
        ))

def actions() -> None:
    for (key, value) in dict(
        GHA_VERSION=__version__,
    ).items():
        print(f"{key}={value}")
