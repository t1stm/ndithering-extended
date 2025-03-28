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

## 🚀 Usage

Grab the latest [Prebuilt Release](https://github.com/Tremeschin/nVibrant/releases), download from your **Package Manager** or [Build it Yourself](#-compiling). Remember to run `chmod +x nvibrant*` to mark the file as executable!

<sup><b>Note:</b> You might need to set `nvidia_drm.modeset=1` kernel parameter, but I think it's enabled by default on recent drivers.</sup>

### Basic usage

**Inputs**: Vibrance Levels are numbers from `-1024` to `1023` that determines the intensity of the effect. Zero being the default for all displays at boot, `-1024` grayscale, and `1023` max saturation.

The values are passed as arguments to `nvibrant`, and the **order must match** the **physical outputs** of your GPU (not the index of the video server). For example, I have two monitors on _DisplayPort_ and _HDMI_ in a single GPU and want to set the vibrance to `512` and `1023` respectively:

```sh
$ ./nvibrant 512 1023
Driver version: (570.133.07)

GPU 0:
• (0, HDMI) • Set Vibrance (  512) • Success
• (1, DP  ) • Set Vibrance ( 1023) • Success
• (2, DP  ) • Set Vibrance (    0) • None
• (3, DP  ) • Set Vibrance (    0) • None
• (4, DP  ) • Set Vibrance (    0) • None
• (5, DP  ) • Set Vibrance (    0) • None
• (6, DP  ) • Set Vibrance (    0) • None
```

If a number is not passed for the Nth physical output, nvibrant will default to zero. When no argument is passed, it will effectively clear the vibrance for all outputs. `None` means the output is disconnected.

You might have a display only at the later ports, in which case use as:

```sh
$ ./nvibrant 0 0 0 0 1023
Driver version: (570.133.07)

GPU 0:
• (0, HDMI) • Set Vibrance (    0) • None
• (1, DP  ) • Set Vibrance (    0) • None
• (2, DP  ) • Set Vibrance (    0) • None
• (3, DP  ) • Set Vibrance (    0) • None
• (4, DP  ) • Set Vibrance (    0) • None
• (5, DP  ) • Set Vibrance ( 1023) • Success
• (6, DP  ) • Set Vibrance (    0) • None
```

### Multiple Displays on Multiple GPUs

If you have multiple displays on multiple GPUs, it _should_ work too: _(Feedback welcome!)_

```sh
$ ./nvibrant 0 100 512 1023
Driver version: (570.133.07)

GPU 0:
• (0, HDMI) • Set Vibrance (    0) • Success
• (1, DP  ) • Set Vibrance (  100) • Success

GPU 1:
• (0, HDMI) • Set Vibrance (  512) • Success
• (1, DP  ) • Set Vibrance ( 1023) • Success
```

### Common errors

- If you get a _"Driver version mismatch"_ or `ioctl` errors, maybe try rebooting (if you haven't) since the last driver update. Otherwise, you can force the version with `NVIDIA_DRIVER_VERSION=x.y.z`. It must match what `/dev/nvidia-modeset` expects.

- Albeit unlikely™, if NVIDIA changes the order of the enum items in the driver, nVibrant might not work correctly.

<sup><b>❤️ Consider</b> [supporting](https://github.com/sponsors/Tremeschin/) my work, this took 14 hours to figure out and implement :)</sup>

## 📦 Compiling

Clone this repository and its submodules with:

- `git clone https://github.com/Tremeschin/nVibrant --recurse-submodules`

Install [Meson](https://mesonbuild.com/) and [Ninja](https://ninja-build.org/) build systems from your Distro. Alternatively, install [uv](https://docs.astral.sh/uv), run `uv sync`, activate the venv and run:

1. Configure: `meson setup build --buildtype release`
2. Compile: `ninja -C build`

You should have the executable located at `build/nvibrant` for the submodule's driver.

## ⭐️ Future work

Integrating this work directly in [libvibrant](https://github.com/libvibrant/) would be the ideal solution, although matching the nvidia driver version could be annoying for a generalized solution. Feel free to base off this code for an upstream solution and PR, in the meantime, here's some local improvements that could be made:

- Make an actual CLI interface with `--help`, `--version`, etc.
- Package the binary in many linux distros (help needed!)
- Save the current values to restore it later.
- I am _probably_ not doing safe-C code or mallocs right :^)

Contributions are welcome if you are more C/C++ savy than me! 🙂
