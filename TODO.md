# TODO

## high

- Implement real camera and capture-card input to replace the current testcard-only `VIDEO SOURCE` model.
- Restore multi-window monitor outputs so each configured monitor can render independently, like `createMonitor()` in `tv_wall_mapper/src/ofApp.cpp`.
- Add NDI receive/send support to cover the `ofxNDI` workflow from the source project.

## medium

- Replace the text-overlay controls with a proper desktop UI that exposes the full config surface from the original ImGui panel.
- Load adapted GLSL shader files from `assets/` instead of keeping the Python-port shader embedded in `src/main.py`.
- Add validation around `tv_first`, `tv_number`, and negative rectangle sizes so unusual layouts are easier to edit safely.

## low

- Add per-monitor fullscreen and output-display selection.
- Carry over more of the original status/help wording from the openFrameworks UI.
- Package the port with platform-specific launch instructions or frozen binaries.
