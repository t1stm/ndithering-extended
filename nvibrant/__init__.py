import os
import shutil
import subprocess
import sys
from functools import cache
from pathlib import Path

from packaging.version import Version

from nvibrant.version import __version__

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

# # Subprocess

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

def rsdir(path: Path) -> Path:
    return mkdir(rmdir(path))

# # Drivers

@cache
def get_driver() -> Version:
    variable: str = "NVIDIA_DRIVER_VERSION"

    # Safety fallback or override with environment variable
    if (force := os.getenv(variable)):
        return Version(force)

    # Seems to be a common and stable path to get the information
    elif (file := Path("/sys/module/nvidia/version")).exists():
        return Version(file.read_text("utf8").strip())

    print("Could not find the current driver version in /sys/module/nvidia/version")
    print(f"• Run with '{variable}=x.y.z nvibrant' to set or force it")
    sys.exit(1)

@cache
def get_versions() -> dict[Version, Path]:
    """Compiled binary versions to their paths"""
    versions = dict()

    # eg "nvibrant-linux-amd64-515.43.04-v1.0.4.bin"
    for file in RESOURCES.glob("*.bin"):
        version = Version(file.stem.split("-")[3])
        versions[version] = file

    return versions

def get_best() -> tuple[Version, Path]:
    """
    Get the highest compiled version that is (or should be) compatible with the
    current driver. Mismatches have a good chance of working even across major
    releases, this makes it so that patch bumps don't need a new build every
    time. You can't win if you don't play otherwise, right?
    """
    options = get_versions()
    current = get_driver()
    optimal = max(x for x in options if x <= current)
    return (optimal, options[optimal])
