from __future__ import annotations

from pathlib import Path


class ShaderManager:
    def __init__(self, shader_dir: Path) -> None:
        self.shader_dir = shader_dir
        self.cache: dict[str, tuple[str, str]] = {}

    def load_sources(self, layout: str) -> tuple[str, str]:
        if layout not in self.cache:
            vertex = (self.shader_dir / "default.vert").read_text(encoding="utf-8")
            fragment = (self.shader_dir / f"{layout}.frag").read_text(encoding="utf-8")
            self.cache[layout] = vertex, fragment
        return self.cache[layout]
