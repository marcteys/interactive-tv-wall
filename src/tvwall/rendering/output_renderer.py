from __future__ import annotations

from array import array

import moderngl
from PIL import Image

from tvwall.domain.models import AppState, Rect
from tvwall.rendering.shader_manager import ShaderManager
from tvwall.services.layout_service import LayoutService
from tvwall.services.source_service import SourceService


class OutputRenderer:
    def __init__(self, ctx: moderngl.Context, shader_manager: ShaderManager) -> None:
        self.ctx = ctx
        self.shader_manager = shader_manager
        self.programs: dict[str, moderngl.Program] = {}
        self.texture: moderngl.Texture | None = None
        self.last_source_revision = -1
        quad_data = array(
            "f",
            (
                -1.0, -1.0, 0.0, 0.0,
                1.0, -1.0, 1.0, 0.0,
                -1.0, 1.0, 0.0, 1.0,
                1.0, 1.0, 1.0, 1.0,
            ),
        ).tobytes()
        self.quad_buffer = self.ctx.buffer(quad_data)
        self.vertex_arrays: dict[str, moderngl.VertexArray] = {}
        self.ctx.enable(moderngl.BLEND)

    def invalidate(self) -> None:
        self.last_source_revision = -1

    def _get_program(self, layout: str) -> moderngl.Program:
        if layout not in self.programs:
            vertex, fragment = self.shader_manager.load_sources(layout)
            program = self.ctx.program(vertex_shader=vertex, fragment_shader=fragment)
            self.programs[layout] = program
            self.vertex_arrays[layout] = self.ctx.simple_vertex_array(program, self.quad_buffer, "in_pos", "in_uv")
        return self.programs[layout]

    def _configure_draw_state(self) -> None:
        self.ctx.screen.use()
        self.ctx.disable(moderngl.DEPTH_TEST)
        self.ctx.disable(moderngl.CULL_FACE)
        self.ctx.enable(moderngl.BLEND)

    def _ensure_texture(self, image: Image.Image) -> None:
        flipped = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        if self.texture is None or self.texture.size != image.size:
            if self.texture is not None:
                self.texture.release()
            self.texture = self.ctx.texture(image.size, 3, flipped.tobytes())
            self.texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
            self.texture.repeat_x = False
            self.texture.repeat_y = False
        else:
            self.texture.write(flipped.tobytes())

    def ensure_source(self, state: AppState, source_service: SourceService) -> None:
        if state.source_revision == self.last_source_revision:
            return
        image = source_service.build_source_image(state)
        self._ensure_texture(image)
        self.last_source_revision = state.source_revision

    @staticmethod
    def _set_uniform(program: moderngl.Program, name: str, value: object) -> bool:
        try:
            program[name] = value
        except KeyError:
            return False
        return True

    @staticmethod
    def _write_uniform(program: moderngl.Program, name: str, data: bytes) -> bool:
        try:
            program[name].write(data)
        except KeyError:
            return False
        return True

    def render(self, state: AppState, rect: Rect) -> None:
        if self.texture is None or rect.width <= 0 or rect.height <= 0:
            return
        monitor = state.active_monitor
        program = self._get_program(monitor.tv_layout)
        packed, safe_count = LayoutService.pack_tv_uniforms(
            state.config.tv_mappings,
            max(0, monitor.tv_first - 1),
            monitor.tv_number,
        )
        self._configure_draw_state()
        self.ctx.viewport = (int(rect.x), int(rect.y), int(rect.width), int(rect.height))
        self.texture.use(0)
        self._set_uniform(program, "u_tex0", 0)
        self._set_uniform(program, "u_canvas", (state.config.canvas_width, state.config.canvas_height))
        self._set_uniform(program, "u_tv_count", safe_count)
        self._write_uniform(program, "u_tvdata", packed)
        self.vertex_arrays[monitor.tv_layout].render(moderngl.TRIANGLE_STRIP)

    def release(self) -> None:
        if self.texture is not None:
            self.texture.release()
            self.texture = None
        for vao in self.vertex_arrays.values():
            vao.release()
        self.vertex_arrays.clear()
        for program in self.programs.values():
            program.release()
        self.programs.clear()
        self.quad_buffer.release()
