#!/usr/bin/env python3
"""Create a lightweight inventory of an openFrameworks project for migration."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

OF_METHODS = [
    "setup", "update", "draw", "exit", "keyPressed", "keyReleased",
    "mouseMoved", "mouseDragged", "mousePressed", "mouseReleased",
    "mouseEntered", "mouseExited", "windowResized", "dragEvent", "gotMessage"
]

OF_SYMBOL_PATTERNS = {
    "graphics_2d": [r"ofDraw", r"ofSetColor", r"ofBackground", r"ofPath", r"ofPolyline"],
    "opengl_3d": [r"ofEasyCam", r"ofCamera", r"ofMesh", r"ofVbo", r"ofShader", r"ofFbo", r"ofLight"],
    "image_video": [r"ofImage", r"ofVideo", r"ofVideoGrabber", r"ofPixels", r"ofTexture"],
    "audio": [r"ofSound", r"audioIn", r"audioOut", r"ofSoundStream", r"ofFft"],
    "gui": [r"ofxGui", r"ofParameter", r"ofxPanel"],
    "serial_hardware": [r"ofSerial", r"ofArduino", r"ofxArduino"],
    "network": [r"ofxOsc", r"ofURLFileLoader", r"ofHttp", r"ofxTCP", r"ofxUDP"],
    "math_simulation": [r"ofVec", r"glm::", r"ofNoise", r"ofRandom", r"ofMap", r"ofLerp"],
}

TEXT_EXTENSIONS = {".cpp", ".h", ".hpp", ".cxx", ".cc", ".frag", ".vert", ".glsl", ".make", ".txt", ".md", ".json", ".xml", ".plist"}
ASSET_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".mp3", ".wav", ".aiff", ".mp4", ".mov", ".ttf", ".otf", ".obj", ".ply", ".dae"}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def relative_files(root: Path):
    for path in root.rglob("*"):
        if path.is_file():
            rel = path.relative_to(root)
            if any(part.startswith(".") and part not in {".vscode", ".github", ".copilot"} for part in rel.parts):
                continue
            yield path, str(rel)


def detect_methods(text: str):
    found = []
    for name in OF_METHODS:
        if re.search(r"\b(?:void\s+)?(?:ofApp::)?" + re.escape(name) + r"\s*\(", text):
            found.append(name)
    return sorted(set(found))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_root", nargs="?", default=".")
    parser.add_argument("--output", default="of_project_inventory.json")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    files = []
    addons = []
    methods = set()
    categories = {key: [] for key in OF_SYMBOL_PATTERNS}
    assets = []
    shaders = []

    for path, rel in relative_files(root):
        suffix = path.suffix.lower()
        if suffix in TEXT_EXTENSIONS or path.name in {"addons.make", "config.make"}:
            text = read_text(path)
            files.append({"path": rel, "kind": "text", "bytes": path.stat().st_size})
            methods.update(detect_methods(text))
            if path.name == "addons.make":
                addons.extend([line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")])
            for category, patterns in OF_SYMBOL_PATTERNS.items():
                hits = []
                for pattern in patterns:
                    if re.search(pattern, text):
                        hits.append(pattern)
                if hits:
                    categories[category].append({"file": rel, "patterns": hits})
            if suffix in {".frag", ".vert", ".glsl"}:
                shaders.append(rel)
        elif suffix in ASSET_EXTENSIONS:
            assets.append({"path": rel, "bytes": path.stat().st_size})
            files.append({"path": rel, "kind": "asset", "bytes": path.stat().st_size})

    present_categories = [key for key, value in categories.items() if value]
    suggested_type = "hybrid"
    if present_categories == ["math_simulation"]:
        suggested_type = "algorithmic"
    elif "opengl_3d" in present_categories:
        suggested_type = "opengl_or_shader_graphics"
    elif "image_video" in present_categories:
        suggested_type = "camera_video_or_image_processing"
    elif "audio" in present_categories:
        suggested_type = "audio"
    elif "serial_hardware" in present_categories:
        suggested_type = "hardware_or_serial"
    elif "graphics_2d" in present_categories:
        suggested_type = "2d_graphics_or_generative_art"

    inventory = {
        "project_root": str(root),
        "files": files,
        "addons": sorted(set(addons)),
        "lifecycle_methods": sorted(methods),
        "detected_categories": present_categories,
        "category_evidence": categories,
        "assets": assets,
        "shaders": shaders,
        "suggested_project_type": suggested_type,
        "recommended_next_step": "Ask the VS Code agent to generate the Python app at the repository root using convertor/.github/copilot-instructions.md and convertor/docs/framework-selection.md."
    }

    output = Path(args.output)
    output.write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    print(f"Wrote {output}")
    print(f"Suggested project type: {suggested_type}")
    if addons:
        print("Addons: " + ", ".join(sorted(set(addons))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
