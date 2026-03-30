# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

mpv-webm is a Lua script plugin for the [mpv](https://mpv.io/) media player that provides an interactive UI for encoding video clips to WebM and other formats. The source is written in [MoonScript](https://moonscript.org/) (which transpiles to Lua) and bundled into a single `build/webm.lua` file.

## Build Commands

```bash
# Build the plugin (requires moonscript)
make

# Build using nix-shell if moonc is not in PATH
nix-shell -p luaPackages.moonscript --run "make"

# Install to ~/.config/mpv/scripts/
make install

# Clean build artifacts
make clean
```

## Testing

Tests use Python's unittest framework and communicate with mpv via IPC socket:

```bash
# Run all tests (from project root)
cd tests && python run_tests.py

# Run a single test file
cd tests && python -m unittest testcases/test_basic_encode.py

# Tests require: mpv, python3, and the built webm.lua
```

The test environment is also available via Nix: `tests/default.nix`.

## Architecture

### Build Process

All `.moon` files in `src/` are **concatenated in Makefile order** into a single `build/webm_bundle.moon`, then compiled with `moonc`. This bundle is then prepended with `src/requires.lua`, `src/options.lua`, and `src/base64.lua` to produce `build/webm.lua`.

**Important**: Because all `.moon` files are bundled, there are no `require` calls between them — they behave as a single file. Source order in the Makefile is significant. Every `.moon` file must end with a blank line.

### Module Structure

- **`src/requires.lua`** — loads mpv API globals (`mp`, `mp.assdraw`, `mp.msg`, `mp.utils`, `mp.options`)
- **`src/options.lua`** — all user-configurable options (keybind, output dir, format, bitrate, etc.)
- **`src/base64.lua`** — base64 utilities
- **`src/util.moon`** — shared helpers: messaging, path formatting, filename templating, property expansion
- **`src/encode.moon`** — core encoding pipeline: builds the ffmpeg command from tracks, filters, format settings
- **`src/main.moon`** — entry point; registers the `Shift+W` keybind

### Format System

`src/formats/base.moon` defines an abstract `Format` class. Each codec subclasses it:

| File | Formats |
|------|---------|
| `formats/webm.moon` | VP8, VP9 |
| `formats/avc.moon` | H.264 (x264, NVENC) |
| `formats/av1.moon` | AV1 |
| `formats/hevc.moon` | HEVC/H.265 |
| `formats/mp3.moon` | MP3 (audio-only) |
| `formats/gif.moon` | GIF |
| `formats/avif.moon` | AVIF |
| `formats/animated_webp.moon` | Animated WebP |
| `formats/rawvideo.moon` | Raw video/PCM |

### UI Page System

Pages are OSD overlays with keybinds and mpv property observers. `src/Page.moon` is the abstract base class. Pages:

- **`MainPage`** — top-level menu; set start/end times, crop, preview, encode
- **`CropPage`** — interactive mouse-driven crop selection
- **`EncodeOptionsPage`** — scrollable options list (int/bool/list types)
- **`PreviewPage`** — ab-loop preview with applied filters
- **`EncodeWithProgress`** — live ffmpeg progress display

### Dev Workflow

The `README.md` describes an isolated mpv dev config at `~/.config/mpv-dev/` with a symlinked `webm.lua`. After editing sources, rebuild and test with `mpv-dev /path/to/video.mp4`.
