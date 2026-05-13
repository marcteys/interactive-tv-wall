# TODO

## high

- Implement real camera and capture-card input to replace the current testcard-only `VIDEO SOURCE` model.
- Restore multi-window monitor outputs so each configured monitor can render independently, like `createMonitor()` in `tv_wall_mapper/src/ofApp.cpp`.
- Add NDI receive/send support to cover the `ofxNDI` workflow from the source project.

## medium

- Add richer source handling beyond testcards and generated map-test content.
- Add real monitor/output discovery and reflect it in the single-window monitor editor.
- Add more UI smoke coverage around the control panel behavior.

## low

- Add per-monitor fullscreen and output-display selection.
- Carry over more of the original help wording and tooltips from the openFrameworks UI.
- Package the port with platform-specific launch instructions or frozen binaries.
