from __future__ import annotations

from pathlib import Path

import moderngl
import pyglet
from pyglet import gl
from pyglet.window import key, mouse

from tvwall.app.controller import AppController
from tvwall.rendering import MapPreviewRenderer, OutputRenderer, ShaderManager, ViewportLayout
from tvwall.services import SourceService
from tvwall.ui import ControlPanelView, PanelAction


class MapperWindow(pyglet.window.Window):
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.controller = AppController(project_root / "config.json")
        config = gl.Config(double_buffer=True, major_version=3, minor_version=3, depth_size=24)
        super().__init__(1400, 900, "TV Wall Mapper", resizable=True, config=config)
        self.ctx = moderngl.create_context()
        self.ctx.clear(0.05, 0.05, 0.07, 1.0)
        shader_dir = project_root / "assets" / "shaders" / "glsl"
        self.source_service = SourceService(project_root / "assets" / "source_data")
        self.output_renderer = OutputRenderer(self.ctx, ShaderManager(shader_dir))
        self.map_renderer = MapPreviewRenderer()
        self.panel = ControlPanelView()
        pyglet.clock.schedule_interval(self._tick, 1.0 / max(self.controller.state.config.framerate, 1))

    def _tick(self, dt: float) -> None:
        self.output_renderer.ensure_source(self.controller.state, self.source_service)

    def _layout(self) -> ViewportLayout:
        return ViewportLayout.compute(self.width, self.height)

    def on_draw(self) -> None:
        self.clear()
        self.ctx.clear(0.05, 0.05, 0.07, 1.0)
        layout = self._layout()
        state = self.controller.state

        self.panel.draw(state, layout.panel_rect)
        if not state.config.hide_preview:
            self.output_renderer.ensure_source(state, self.source_service)
            self.output_renderer.render(state, layout.output_rect)
            self.ctx.viewport = (0, 0, self.width, self.height)
        if not state.config.hide_maptest:
            self.map_renderer.draw(state, layout.map_rect)

        pyglet.text.Label("OUTPUT PREVIEW", x=layout.output_rect.x, y=layout.output_rect.top + 8, color=(255, 255, 255, 255)).draw()
        pyglet.text.Label("MAP PREVIEW", x=layout.map_rect.x, y=layout.map_rect.top + 8, color=(255, 255, 255, 255)).draw()
        status = f"{state.status_message} | Source: {state.current_source_index + 1}/{len(self.source_service.labels())} | Grid: {state.grid_size}mm"
        pyglet.text.Label(status, x=layout.footer_rect.x, y=layout.footer_rect.y + 8, color=(215, 215, 225, 255)).draw()
        if state.show_framerate:
            fps = round(pyglet.clock.get_fps())
            pyglet.text.Label(f"FPS: {fps}", x=self.width - 88, y=14, color=(255, 90, 90, 255)).draw()

    def _apply_window_state(self) -> None:
        if self.fullscreen != self.controller.state.active_monitor.is_fullscreen:
            self.set_fullscreen(self.controller.state.active_monitor.is_fullscreen)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        action = self.panel.hit_test(x, y)
        if action is not None:
            self.controller.handle_action(action)
            self._apply_window_state()
            return
        layout = self._layout()
        if button == mouse.LEFT or button == mouse.RIGHT:
            self.controller.begin_drag(layout.map_rect, x, y)

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int) -> None:
        layout = self._layout()
        resize = bool(buttons & mouse.RIGHT or modifiers & key.MOD_SHIFT)
        self.controller.drag_selected(layout.map_rect, x, y, resize)

    def on_mouse_scroll(self, x: int, y: int, scroll_x: float, scroll_y: float) -> None:
        if self._layout().panel_rect.contains(x, y):
            self.panel.scroll(-scroll_y * 24)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        alt_pressed = bool(modifiers & key.MOD_ALT)
        shift_pressed = bool(modifiers & key.MOD_SHIFT)
        if symbol == key.F:
            self.controller.handle_action(PanelAction("toggle_fullscreen"))
            self._apply_window_state()
            return
        if symbol == key.R:
            self.controller.handle_action(PanelAction("toggle_framerate"))
            return
        if symbol == key.S:
            self.controller.save()
            return
        if symbol == key.L:
            self.controller.load()
            self._apply_window_state()
            return
        if symbol == key.I:
            self.controller.cycle_source()
            return
        if symbol == key.M:
            self.controller.set_source(2)
            return
        if symbol in (key._1, key._2, key._3):
            layout = {key._1: 0, key._2: 1, key._3: 2}[symbol]
            self.controller.handle_action(PanelAction("set_layout", {"index": layout}))
            return
        if alt_pressed:
            if symbol == key.LEFT:
                self.controller.select_relative_tv(-1)
            elif symbol == key.RIGHT:
                self.controller.select_relative_tv(1)
            elif symbol == key.UP:
                self.controller.cycle_grid(-1)
            elif symbol == key.DOWN:
                self.controller.cycle_grid(1)
            return

        resize = shift_pressed
        if symbol == key.LEFT:
            self.controller.keyboard_move(x_direction=-1, resize=resize)
        elif symbol == key.RIGHT:
            self.controller.keyboard_move(x_direction=1, resize=resize)
        elif symbol == key.UP:
            self.controller.keyboard_move(y_direction=-1, resize=resize)
        elif symbol == key.DOWN:
            self.controller.keyboard_move(y_direction=1, resize=resize)
