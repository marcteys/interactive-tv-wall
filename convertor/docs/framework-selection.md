# Framework selection guide

Use this guide when choosing the Python target stack for an openFrameworks translation.

## Decision table

| openFrameworks project evidence | Preferred Python target | Typical dependencies |
|---|---|---|
| `ofDraw*`, `ofSetColor`, `ofBackground`, mouse/keyboard interaction, simple 2D sketches | `pygame` or `py5` | `pygame` or `py5` |
| Processing-like generative art, simple frame loop, drawing primitives | `py5` | `py5`, `numpy` |
| Input-heavy 2D game or installation interface | `pygame` | `pygame`, `numpy` |
| `ofShader`, `ofFbo`, `ofVbo`, `ofMesh`, `ofEasyCam`, custom GLSL | `moderngl` with `glfw` or `pyglet` | `moderngl`, `glfw`, `numpy`, `pyrr` |
| `ofVideoGrabber`, `ofImage`, `ofPixels`, blob tracking, computer vision | OpenCV stack | `opencv-python`, `numpy` |
| `ofSoundStream`, `audioIn`, `audioOut`, FFT, waveform analysis | Python audio stack | `sounddevice`, `numpy`, `scipy` |
| `ofxOsc` | OSC stack | `python-osc` |
| MIDI addons | MIDI stack | `mido`, `python-rtmidi` |
| `ofSerial`, Arduino, sensors | serial stack | `pyserial` |
| Network requests, APIs, HTTP | web client stack | `requests`, `websockets` when needed |
| Minimal algorithmic code without rendering | native Python | standard library, `numpy` if math-heavy |

## Selection rules

1. Prefer the smallest stack that can preserve behavior.
2. Keep Python native where possible, but do not force native-only Python when rendering, real-time interaction, audio, video, or hardware access requires libraries.
3. For mixed projects, choose a primary runtime and add targeted dependencies. Example: `pygame` plus `opencv-python` for a 2D camera installation.
4. Keep shader-heavy projects shader-heavy: port the host application to `moderngl`, retain GLSL files, and adapt uniforms/textures.
5. Record both the chosen and rejected stacks in `MIGRATION.md`.

## Default fallback

When project evidence is weak, create a minimal Python structure using an `App` class and no external dependencies. Add TODOs for any missing rendering/audio/video assumptions.
