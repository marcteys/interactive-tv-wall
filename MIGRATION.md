# Migration Notes

## Source files inspected

- `tv_wall_mapper/src/main.cpp`
- `tv_wall_mapper/src/ofApp.h`
- `tv_wall_mapper/src/ofApp.cpp`
- `tv_wall_mapper/addons.make`
- `tv_wall_mapper/README.md`
- `tv_wall_mapper/bin/data/glsl/*.frag`
- `tv_wall_mapper/bin/data/glsl/default.vert`
- `convertor/of_project_inventory.json`

## openFrameworks features detected

- `ofShader`, `ofFbo`, `ofTexture`
- `ofImage`
- `ofVideoGrabber`
- JSON config load/save via `ofxJSON`
- ImGui control panel via `ofxImGui`
- NDI receive/send via `ofxNDI`
- Multi-window output using GLFW windows
- Mouse and keyboard mapping controls

## Framework decision

Chosen stack:
- `pyglet`
- `moderngl`
- `Pillow`
- `pytest`

Why:
- the source project is primarily an OpenGL mapping tool with shader-based output layouts.
- `moderngl` preserves the important rendering model better than a simpler 2D-only stack.
- `pyglet` provides cross-platform windowing and input without pulling in a larger engine.

Rejected alternatives:
- `pygame`: easier for 2D UI, but a weaker fit for shader-first output rendering.
- `py5`: good for sketch-style graphics, but not ideal for preserving the original multi-pass mapping design.
- `opencv-python`: useful later for camera capture, but not sufficient as the main runtime.

## API mapping

| openFrameworks | Python port |
|---|---|
| `setup()` | `MapperWindow.__init__()` plus controller/service initialization |
| `update()` | `MapperWindow._tick()` with renderer-side source refresh |
| `draw()` | `MapperWindow.on_draw()` |
| `keyPressed()` / `keyReleased()` | `MapperWindow.on_key_press()` routed through `AppController` |
| `mousePressed()` / `mouseDragged()` | `MapperWindow` event bridge + `LayoutService` drag math |
| `jsonLoad()` / `jsonSave()` | `ConfigRepository.load()` / `ConfigRepository.save()` |
| `ofShader` | disk-loaded GLSL managed by `ShaderManager` and `OutputRenderer` |
| `ofImage` testcards | `Pillow` images uploaded as textures |
| `mapTest` FBO drawing | `SourceService` map-test image generation plus `MapPreviewRenderer` |
| ImGui settings panel | custom `pyglet` control panel in `src/tvwall/ui/` |

## Behavioral equivalence notes

- Preserved:
  - TV rectangle mapping stored in millimeters.
  - `1`, `2x2`, and `3x3` layout modes.
  - Rotation behavior when a TV rectangle is taller than it is wide.
  - Core keyboard and mouse editing semantics.
  - JSON config structure close to the original app.
  - Disk-based shader loading for the Python runtime.
  - Automated validation of core mapping logic via `pytest`.

- Partially preserved:
  - The original monitor-oriented workflow is available inside a single-window control panel rather than through real extra output windows.
  - The shader logic is adapted for Python and `moderngl`, rather than using the raw openFrameworks shader files directly.

- Not yet preserved:
  - Camera input via `ofVideoGrabber`
  - NDI input/output
  - Separate GLFW windows per monitor output

## Manual migration items

- Wire real video inputs into the `VIDEO SOURCE` model.
- Add optional NDI support behind a feature flag or extra requirements file.
- Expand single-window preview into real multi-window monitor outputs.
- Consider broader UI smoke coverage if the control panel grows more complex.
