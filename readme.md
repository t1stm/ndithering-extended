<div align="center">
  <img src="https://raw.githubusercontent.com/material-extensions/vscode-material-icon-theme/refs/heads/main/icons/cuda.svg" width="210">
  <h1>nVibrant</h1>
  <p>Configure NVIDIA's Digital Vibrance on Wayland</p>
</div>

> [!IMPORTANT]
> This repository is a proof of concept that will be improved over time, e.g. proper CLI and distro packaging are WIP. Contributions are welcome, as I'm not primarily a C/C++ developer 🙂

## 🔥 Description

**NVIDIA GPUs** have a nice feature called **Digital Vibrance** that increases the colors saturation of the display. The option is readily available on [nvidia-settings](https://github.com/NVIDIA/nvidia-settings/) in Linux, but is too coupled with `libxnvctrl`. Therefore, it is "exclusive" to the X11 display server, making it unavailable on Wayland. But I don't want dull colors :^)

An interesting observation is that the setting persists after modifying it on X11 and then switching to Wayland. I theorized [[1]](https://github.com/libvibrant/vibrantLinux/issues/27#issuecomment-2729822152) [[2]](https://www.reddit.com/r/archlinux/comments/1gx1hir/comment/mhpe2pk/?context=3) it was possible to call some shared library or interface to configure it directly in their driver, independently of the display server. And indeed, it is possible!

This repository uses `nvidia-modeset` and `nvkms` headers found at [NVIDIA/open-gpu-kernel-modules](https://github.com/NVIDIA/open-gpu-kernel-modules/) to make [ioctl](https://en.wikipedia.org/wiki/Ioctl) calls in the `/dev/nvidia-modeset` device for configuring display attributes. These headers are synced with the proprietary releases, should work fine if you're on any of `nvidia-dkms`, `nvidia-open` or `nvidia`.

**Note**: A future (and intended) way to will be through [NVML](https://developer.nvidia.com/management-library-nvml), as evident by some [nvidia-settings](https://github.com/NVIDIA/nvidia-settings/blob/6c755d9304bf4761f2b131f0687f0ebd1fcf7cd4/src/libXNVCtrlAttributes/NvCtrlAttributesNvml.c#L1235) comments.

**Warn**: The binary is bound to the submodule's NVIDIA Driver Version, e.g. `570.133.07`

## 🚀 Usage

Grab the latest [prebuilt release](https://github.com/Tremeschin/nVibrant/releases) for your matching NVIDIA driver version, [build it yourself](#-compiling) or download from your package manager. You might need to `chmod +x nvibrant*` to mark the file as executable!

<sup><b>Note:</b> You might need to set `nvidia_drm.modeset=1` kernel parameter, but I think it's enabled by default on recent drivers.</sup>

**Inputs**: Vibrance levels are numbers from `-1024` to `1023` for each display. If a number is not passed for the Nth display, it will default to zero. See the examples below:

```sh
# Maximum vibrance for display 0
./nvibrant 1023

# Maximum vibrance for display 1
./nvibrant 0 1023

# Medium vibrance for both displays
./nvibrant 512 512

# Grayscale on all three monitors
./nvibrant -1024 -1024 -1024
```

The order of displays should match the physical connections of the GPU, experiment with it!

<sup><b>❤️ Consider</b> [supporting](https://github.com/sponsors/Tremeschin/) my work, this took 14 hours to figure out and implement :)</sup>

## 📦 Compiling

Clone this repository and its submodules with:

- `git clone https://github.com/Tremeschin/nVibrant --recurse-submodules`

Install [Meson](https://mesonbuild.com/) and [Ninja](https://ninja-build.org/) build systems from your Distro. Alternatively, install [uv](https://docs.astral.sh/uv) and run `uv tool install meson` and `uv tool install ninja`, following any instructions for adding to PATH, and run:

1. Configure: `meson setup build --buildtype release`
2. Compile: `ninja -C build`

You should have the executable located at `build/nvibrant` for the submodule's driver.

For building multiple driver versions, you can run `uv run nvibrant-build`

## ⭐️ Future work

Integrating this work directly in [libvibrant](https://github.com/libvibrant/) would be the ideal solution, although matching the nvidia driver version could be annoying for a generalized solution. Feel free to base off this code for an upstream solution and PR, in the meantime, here's some local improvements that could be made:

- Simplify the code, some lists enumerations are opaque and flag-like
- List displays and show their info on the command line
- Make an actual CLI interface with `--help`, `--version`, etc.
- Package the binary in many linux distros (help needed!)
- Save the current values to restore it later.
- Improve the Readme organization, explanations.
- I am _probably_ not doing safe-C code or mallocs right :^)

Contributions are welcome if you are more C/C++ savy than me! 🙂
