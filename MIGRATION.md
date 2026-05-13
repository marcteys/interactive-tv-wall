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
| `setup()` | `MapperWindow.__init__()` |
| `update()` | `MapperWindow._tick()` |
| `draw()` | `MapperWindow.on_draw()` |
| `keyPressed()` / `keyReleased()` | `MapperWindow.on_key_press()` |
| `mousePressed()` / `mouseDragged()` | `MapperWindow.on_mouse_press()` / `MapperWindow.on_mouse_drag()` |
| `jsonLoad()` / `jsonSave()` | `AppConfig.from_json()` / `MapperWindow.save_config()` |
| `ofShader` | `moderngl.Program` |
| `ofImage` testcards | `Pillow` images uploaded as textures |
| `mapTest` FBO drawing | PIL-generated map texture plus pyglet preview overlay |

## Behavioral equivalence notes

- Preserved:
  - TV rectangle mapping stored in millimeters.
  - `1`, `2x2`, and `3x3` layout modes.
  - Rotation behavior when a TV rectangle is taller than it is wide.
  - Core keyboard and mouse editing semantics.
  - JSON config structure close to the original app.

- Partially preserved:
  - Shader behavior is preserved conceptually, but the port uses one Python-side GLSL program instead of loading the original openFrameworks shader files as-is.
  - Only one monitor configuration is previewed live at a time, even though multiple monitor entries can still exist in config data.

- Not yet preserved:
  - Camera input via `ofVideoGrabber`
  - NDI input/output
  - ImGui settings UI
  - Separate GLFW windows per monitor output

## Manual migration items

- Wire real video inputs into the `VIDEO SOURCE` model.
- Add optional NDI support behind a feature flag or extra requirements file.
- Expand single-window preview into real multi-window monitor outputs.
- Revisit shader loading so adapted copies of the original GLSL files can be loaded from disk directly.
