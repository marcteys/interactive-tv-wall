from __future__ import annotations

from pathlib import Path

from tvwall.rendering.shader_manager import ShaderManager
from tvwall.rendering.viewport_layout import ViewportLayout


def test_viewport_layout_has_non_overlapping_sections() -> None:
    layout = ViewportLayout.compute(1400, 900)
    assert layout.panel_rect.width >= 360
    assert layout.output_rect.x > layout.panel_rect.right
    assert layout.map_rect.x == layout.output_rect.x
    assert layout.output_rect.y > layout.map_rect.y


def test_shader_manager_loads_disk_sources() -> None:
    shader_dir = Path(__file__).resolve().parents[1] / "assets" / "shaders" / "glsl"
    manager = ShaderManager(shader_dir)
    vertex, fragment = manager.load_sources("3x3")
    assert "#version 330" in vertex
    assert "u_tvdata" in fragment
