<div align="center">
  <h1>nVibrant</h1>
  <b>Use NVIDIA's Digital Vibrance on Wayland</b>
</div>

> [!IMPORTANT]
> This repository is a proof of concept that will be improved over time. Namely, a command line interface is missing, and I'm blindly setting the maximum Digital Vibrance on _all_ displays. Contributions are welcome, as I'm not primarily a C/C++ developer 🙂

## Description:

NVIDIA GPUs have a feature called Digital Vibrance that increases the color saturation of the display. Configuring is readily available on [nvidia-settings](https://github.com/NVIDIA/nvidia-settings/) in Linux, but is too coupled with `libxnvctrl`. Therefore, it's exclusive to the X11 display server, making it unavailable on Wayland.

An interesting observation is that the setting persists after modifying it on X11 and then switching to Wayland. I theorized [[1]](https://github.com/libvibrant/vibrantLinux/issues/27#issuecomment-2729822152) [[2]](https://www.reddit.com/r/archlinux/comments/1gx1hir/comment/mhpe2pk/?context=3) it was possible to make some driver or interface calls to configure it directly in their driver independent of the display server, and indeed it works!

This repository uses `nvidia-modeset` and `nvkms` headers found at [NVIDIA/open-gpu-kernel-modules](https://github.com/NVIDIA/open-gpu-kernel-modules/) to make [ioctl](https://en.wikipedia.org/wiki/Ioctl) calls in the `/dev/nvidia-modeset` device for setting the Digital Vibrance, independently from the display server in use (Wayland, X11)

**Warn**: The binary is bound to a single NVIDIA Driver Version, currently `570.133.07`.

## Compiling:

Clone this repository and its submodules:

- `git clone https://github.com/Tremeschin/nVibrant --recurse-submodules`

Install [Meson](https://mesonbuild.com/) and [Ninja](https://ninj-build.org/) build systems from your Distro. Alternatively, install [uv](https://docs.astral.sh/uv) and run `uv tool install meson` and `uv tool install ninja`, following any instructions for adding to PATH, and then configure and compile with:

1. `meson build`
2. `ninja -C build`

## Usage:

After compiling, you should have the executable at `build/nvibrant`.

Running it will set the digital vibrance to 100% (value 1023) on all displays, currently. You can edit the source code and change the value at the top from `-1024` to `1023` until a CLI is implemented.

## Future work:

Contributions are welcome if you are more C/C++ savy than me! 🙂

- Simplify the code, some lists enumerations are opaque and flag-like
- How to target different drivers? Maybe tag checkouts automation?
- Command Line Interface (CLI) to set custom values, ideally per display.
- Convert the code to C++? Easier vectors, classes, cli, configs.
- Package the binary in many linux distros (help needed!)
- Save the current values to restore it later.
- Improve the Readme organization, explanations.
- I am _probably_ not doing safe-C code or mallocs right :^)
