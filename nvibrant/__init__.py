import os
import shutil
import subprocess
import sys
from pathlib import Path

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
