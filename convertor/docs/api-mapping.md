# openFrameworks to Python API mapping

Use this table as a migration reference. Adapt to the selected Python framework.

| openFrameworks concept | Python translation strategy |
|---|---|
| `ofApp::setup()` | Initialize `App` state, window, assets, devices, and resources. |
| `ofApp::update()` | Update simulation, timing, inputs, media frames, and non-rendering state. |
| `ofApp::draw()` | Render frame through selected framework. |
| `ofGetElapsedTimef()` | Use `time.perf_counter()` or framework clock. |
| `ofGetFrameNum()` | Maintain `self.frame_count`. |
| `ofGetWidth()`, `ofGetHeight()` | Use window dimensions or stored config values. |
| `ofBackground()` | Clear display/window surface. |
| `ofSetColor()` | Set drawing color or pass color to draw call. |
| `ofDrawCircle`, `ofDrawRectangle`, `ofDrawLine` | Use equivalent primitives in `pygame`, `py5`, or OpenGL draw helpers. |
| `ofImage` | Use `pygame.image`, `PIL`, or OpenCV depending on target stack. |
| `ofVideoGrabber` | Use `cv2.VideoCapture`. |
| `ofShader` | Use `moderngl.Program`; preserve GLSL when feasible. |
| `ofFbo` | Use framebuffer object in `moderngl`; otherwise document limitation. |
| `ofMesh` | Use vertex buffers in `moderngl` or arrays in `numpy`. |
| `ofSoundPlayer` | Use `pygame.mixer`, `sounddevice`, or `pydub` depending on needs. |
| `ofSoundStream` | Use `sounddevice` callbacks. |
| `ofxGui` | Use `dearpygui`, `pygame_gui`, or config files; document deviations. |
| `ofxOsc` | Use `python-osc`. |
| `ofSerial` | Use `pyserial`. |
| `ofRandom`, `ofNoise`, `ofMap`, `ofClamp`, `ofLerp` | Use helper functions in `src/utils.py` or `numpy`. |

## Important migration constraints

- openFrameworks often hides global rendering state; Python ports should make state explicit.
- C++ constructors/destructors should become Python `__init__`, context managers, or explicit setup/cleanup methods.
- Pointer ownership and references should be simplified into Python objects unless resource lifetime is critical.
- Real-time code should avoid unnecessary allocation in per-frame loops.
