# TV Wall Mapper Python Port

## Overview

This is a Python translation of the `tv_wall_mapper` openFrameworks project under `tv_wall_mapper/`.
The port focuses on the core mapping workflow: loading a wall configuration, editing TV rectangles with mouse and keyboard controls, previewing the map, and rendering the mapped output through an OpenGL shader.

## Selected Python stack

- `pyglet`: windowing, input events, text, and 2D overlay drawing.
- `moderngl`: OpenGL rendering for the output preview shader.
- `Pillow`: image loading and generation for testcards and the map-test source.

Why this stack:
- the source app is shader-driven and uses `ofShader` and `ofFbo`, so a GPU-backed Python port is a better fit than a pure CPU blit approach.
- `pyglet` keeps the runtime smaller than recreating the full openFrameworks + ImGui setup in Python for a first working port.

## What works

- Loads and saves a JSON config in the same general shape as the openFrameworks app.
- Uses the original TV-wall mapping concept with `1`, `2x2`, and `3x3` output layouts.
- Includes both shipped testcards and a generated `TESTMAP` source.
- Supports mouse selection, drag-to-move, shift/right-drag resize, and keyboard nudging.
- Shows a live map preview and a shader-based output preview in one desktop window.

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python src/main.py
```

## Controls

- Left click a TV in the map preview to select it.
- Drag with left mouse to move the selected TV.
- Drag with right mouse, or hold `Shift` while dragging, to resize.
- Arrow keys move the selected TV by the current grid size.
- `Shift` + arrow keys resize by the current grid size.
- `Alt` + left/right selects the previous or next TV.
- `Alt` + up/down cycles the grid size.
- `1`, `2`, `3` switch the monitor layout to `1`, `2x2`, `3x3`.
- `I` cycles sources, `M` switches directly to `TESTMAP`.
- `S` saves `config.json`, `L` reloads it.
- `F` toggles fullscreen.

## Assets

Original source assets were copied from `tv_wall_mapper/bin/data/` into [assets/source_data](./assets/source_data).
That includes testcards, icons, and the original GLSL and GLES shader sources for reference.

## Known limitations

- This port intentionally ships as a single-window application. The original app can spawn multiple monitor windows.
- Video capture device enumeration is not implemented yet.
- NDI receive/send is not implemented yet.
- The original ImGui control surface is replaced with keyboard, mouse, and on-screen text.
- The Python app uses an adapted shader host instead of loading the original openFrameworks shader files directly.

See [MIGRATION.md](./MIGRATION.md) and [TODO.md](./TODO.md) for the remaining work.

## Converter assets

The prompt pack, validation scripts, templates, and VS Code helper files used for this migration now live under [convertor](./convertor).
