# openFrameworks to Python translation instructions

You are translating openFrameworks C++ projects or code snippets into complete, runnable Python projects.

## Core objective

Produce a complete Python port, not a loose code excerpt. Always include source code, dependencies, documentation, migration notes, and TODOs for unresolved behavior.

## Inputs you may receive

- A complete openFrameworks project folder.
- Individual `ofApp.h`, `ofApp.cpp`, `main.cpp`, addon files, shader files, assets, or pasted snippets.
- Partial code where some project files are missing.

If files are missing, infer conservatively and record assumptions in `MIGRATION.md` and `TODO.md`.

## Mandatory output structure

Create or update the Python app at the repository root:

```text
./
  README.md
  requirements.txt
  MIGRATION.md
  TODO.md
  src/
    main.py
  assets/
```

Add more modules under `src/` when the project has distinct concerns, such as rendering, simulation, audio, video, input, serial, networking, or utilities.

## Workflow

1. Inspect the project tree. Prefer running `python convertor/scripts/analyze_of_project.py . --output convertor/of_project_inventory.json` if available.
2. Identify openFrameworks lifecycle methods, addons, assets, shaders, input handlers, and external dependencies.
3. Classify the project type.
4. Select the most appropriate Python stack using `convertor/docs/framework-selection.md`.
5. Translate architecture before translating individual lines.
6. Generate the full Python project at the repository root.
7. Add documentation and migration notes.
8. Run or explain validation. Prefer `python convertor/scripts/validate_python_project.py .` if available.
9. Update `TODO.md` with concrete remaining tasks.

## Framework selection policy

Do not default blindly to a single framework. Choose the stack according to the project:

- Minimal algorithmic or non-visual code: Python standard library plus small targeted dependencies.
- 2D sketches, generative art, Processing-like drawing: `py5` or `pygame`.
- Interactive 2D games or input-heavy apps: `pygame`.
- OpenGL, shaders, FBOs, meshes, advanced rendering: `moderngl` plus `glfw` or `pyglet`.
- Camera, image processing, blob tracking: `opencv-python` plus `numpy`.
- Audio input/output, FFT, real-time synthesis: `sounddevice`, `numpy`, `scipy`, or `pyo` when appropriate.
- Data visualization: `matplotlib`, `plotly`, or `pygame`/`py5` depending on interactivity.
- Serial/Arduino/hardware: `pyserial`.
- OSC/MIDI/networking: `python-osc`, `mido`, `python-rtmidi`, `websockets`, or `requests` as needed.

Record the chosen stack and rejected alternatives in `MIGRATION.md`.

## Translation rules

- Preserve behavior over syntax.
- Preserve coordinate systems, timing semantics, frame-based logic, and event handlers.
- Map `setup`, `update`, `draw`, `keyPressed`, `keyReleased`, `mouseMoved`, `mouseDragged`, `mousePressed`, `mouseReleased`, `windowResized`, and similar lifecycle functions into idiomatic Python equivalents.
- Replace openFrameworks global state and free functions with a clear Python `App` class unless a target framework strongly suggests another pattern.
- Keep rendering and update logic separated.
- Preserve asset paths and copy assets into `assets/` when possible.
- For shaders, keep GLSL source files where possible and adapt only the Python host code first.
- For addons, identify each addon and map it to a Python dependency or explicit TODO.
- Never silently drop functionality. If not implemented, add a TODO with the original symbol/function and reason.

## Documentation requirements

`README.md` must include:

- Project purpose.
- Selected Python stack and rationale.
- Installation instructions.
- Run command.
- Notes on assets and external devices.
- Known limitations.

`MIGRATION.md` must include:

- Source files inspected.
- openFrameworks features detected.
- Framework decision.
- API mapping table.
- Behavioral equivalence notes.
- Manual migration items.

`TODO.md` must include:

- Actionable unresolved items.
- Priority labels: `high`, `medium`, `low`.
- Original openFrameworks symbols or files where relevant.

## Quality bar

Generated Python should be readable, modular, and executable after installing `requirements.txt`, except for TODOs explicitly documented. Do not fabricate hardware, API keys, assets, or unavailable data.
