from __future__ import annotations

from pathlib import Path

import pyglet

from tvwall.app.window import MapperWindow


def main() -> None:
    project_root = Path(__file__).resolve().parents[3]
    MapperWindow(project_root)
    pyglet.app.run()
