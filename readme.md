<div align="center">
  <img src="https://raw.githubusercontent.com/material-extensions/vscode-material-icon-theme/refs/heads/main/icons/cuda.svg" width="210">
  <h1>nVibrant</h1>
  <p>Configure NVIDIA's Digital Vibrance on Wayland</p>
</div>

> [!IMPORTANT]
> This repository is a proof of concept that will be improved over time. Namely, a command line interface is missing, and I'm blindly setting the maximum Digital Vibrance on _all_ displays.
>
> Contributions are welcome, as I'm not primarily a C/C++ developer 🙂

## 🔥 Description:

NVIDIA GPUs have a nice feature called Digital Vibrance that increases the colors saturation of the display. The option is readily available on [nvidia-settings](https://github.com/NVIDIA/nvidia-settings/) in Linux, but is too coupled with `libxnvctrl`. Therefore, it is "exclusive" to the X11 display server, making it unavailable on Wayland. But I don't want dull colors :^)

An interesting observation is that the setting persists after modifying it on X11 and then switching to Wayland. I theorized [[1]](https://github.com/libvibrant/vibrantLinux/issues/27#issuecomment-2729822152) [[2]](https://www.reddit.com/r/archlinux/comments/1gx1hir/comment/mhpe2pk/?context=3) it was possible to make some shared library or interface calls to configure it directly in their driver, independent of the display server. And indeed, it is possible!

This repository uses `nvidia-modeset` and `nvkms` headers found at [NVIDIA/open-gpu-kernel-modules](https://github.com/NVIDIA/open-gpu-kernel-modules/) repository to make [ioctl](https://en.wikipedia.org/wiki/Ioctl) calls in the `/dev/nvidia-modeset` device for configuring display attributes.

**Note**: A future (and intended) way to configure this setting will be through [NVIDIA Management Library](https://developer.nvidia.com/management-library-nvml) (NVML), as is evident by some [nvidia-settings](https://github.com/NVIDIA/nvidia-settings/blob/6c755d9304bf4761f2b131f0687f0ebd1fcf7cd4/src/libXNVCtrlAttributes/NvCtrlAttributesNvml.c#L1235) comments. This is a temporary workaround, or perhaps a stable way of doing it through interfacing with the kernel modules.

**Warn**: The binary is bound to a single NVIDIA Driver Version, currently `570.133.07`

## 📦 Compiling:

Clone this repository and its submodules with:

- `git clone https://github.com/Tremeschin/nVibrant --recurse-submodules`

Install [Meson](https://mesonbuild.com/) and [Ninja](https://ninja-build.org/) build systems from your Distro. Alternatively, install [uv](https://docs.astral.sh/uv) and run `uv tool install meson` and `uv tool install ninja`, following any instructions for adding to PATH, and run:

1. Configure: `meson build`
2. Compile: `ninja -C build`

## 🚀 Usage:

After compiling, you should have the executable at `build/nvibrant`

Running it will set the digital vibrance to 100% (value 1023) on all displays, currently. You can edit the source code and change the value at the top from `-1024` to `1023` until a CLI is implemented.

<sup><b>❤️ Consider</b> [supporting](https://github.com/sponsors/Tremeschin/) my work, this took 10 hours to figure out and implement :)</sup>

## ⭐️ Future work:

Integrating this work directly in [libvibrant](https://github.com/libvibrant/) would be the ideal solution, although matching the nvidia driver version could be annoying for a generalized solution. Feel free to base off this code for an upstream solution and PR, in the meantime, here's some local improvements that could be made:

- Simplify the code, some lists enumerations are opaque and flag-like
- How to target different drivers? Maybe tag checkouts automation?
- Command Line Interface (CLI) to set custom values, ideally per display.
- Convert the code to C++? Easier vectors, classes, cli, configs.
- Package the binary in many linux distros (help needed!)
- Save the current values to restore it later.
- Improve the Readme organization, explanations.
- I am _probably_ not doing safe-C code or mallocs right :^)

Contributions are welcome if you are more C/C++ savy than me! 🙂
