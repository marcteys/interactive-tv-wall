from __future__ import annotations

import logging
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
        self.logger = logging.getLogger("tvwall.window")
        self._window_state_sync_pending = False
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
        self.overlay_batch = pyglet.graphics.Batch()
        self.output_label = pyglet.text.Label("OUTPUT PREVIEW", x=0, y=0, batch=self.overlay_batch, color=(255, 255, 255, 255))
        self.map_label = pyglet.text.Label("MAP PREVIEW", x=0, y=0, batch=self.overlay_batch, color=(255, 255, 255, 255))
        self.status_label = pyglet.text.Label("", x=0, y=0, batch=self.overlay_batch, color=(215, 215, 225, 255))
        self.fps_label = pyglet.text.Label("", x=0, y=0, batch=self.overlay_batch, color=(255, 90, 90, 255))
        pyglet.clock.schedule_interval(self._tick, 1.0 / max(self.controller.state.config.framerate, 1))

    def _reschedule_tick(self) -> None:
        pyglet.clock.unschedule(self._tick)
        pyglet.clock.schedule_interval(self._tick, 1.0 / max(self.controller.state.config.framerate, 1))

    def _tick(self, dt: float) -> None:
        try:
            self.output_renderer.ensure_source(self.controller.state, self.source_service)
        except Exception:
            self.controller.state.status_message = "Background refresh failed"
            self.logger.exception("Source refresh failed")

    def _layout(self) -> ViewportLayout:
        return ViewportLayout.compute(self.width, self.height)

    def on_draw(self) -> None:
        try:
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

            self.output_label.text = "OUTPUT PREVIEW"
            self.output_label.x = layout.output_rect.x
            self.output_label.y = layout.output_rect.top + 8
            self.output_label.visible = True
            self.map_label.text = "MAP PREVIEW"
            self.map_label.x = layout.map_rect.x
            self.map_label.y = layout.map_rect.top + 8
            self.map_label.visible = True
            self.status_label.text = (
                f"{state.status_message} | Source: {state.current_source_index + 1}/{len(self.source_service.labels())} | Grid: {state.grid_size}mm"
            )
            self.status_label.x = layout.footer_rect.x
            self.status_label.y = layout.footer_rect.y + 8
            self.status_label.visible = True
            if state.show_framerate:
                fps = round(pyglet.clock.get_fps())
                self.fps_label.text = f"FPS: {fps}"
                self.fps_label.x = self.width - 88
                self.fps_label.y = 14
                self.fps_label.visible = True
            else:
                self.fps_label.visible = False
            self.overlay_batch.draw()
        except Exception:
            self.controller.state.status_message = "Render failed"
            self.logger.exception("Draw failed")

    def _request_window_state_sync(self) -> None:
        if self._window_state_sync_pending:
            return
        self._window_state_sync_pending = True
        pyglet.clock.schedule_once(self._apply_window_state, 0.0)

    def _apply_window_state(self, dt: float = 0.0) -> None:
        self._window_state_sync_pending = False
        desired_fullscreen = self.controller.state.active_monitor.is_fullscreen
        if self.fullscreen != desired_fullscreen:
            self.set_fullscreen(desired_fullscreen)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        action = self.panel.hit_test(x, y)
        if action is not None:
            self.controller.handle_action(action)
            if action.command == "load":
                self._reschedule_tick()
            self._request_window_state_sync()
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
            self._request_window_state_sync()
            return
        if symbol == key.R:
            self.controller.handle_action(PanelAction("toggle_framerate"))
            return
        if symbol == key.S:
            self.controller.save()
            return
        if symbol == key.L:
            self.controller.load()
            self._reschedule_tick()
            self._request_window_state_sync()
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

    def on_close(self) -> None:
        pyglet.clock.unschedule(self._tick)
        pyglet.clock.unschedule(self._apply_window_state)
        try:
            self.output_renderer.release()
        except Exception:
            self.logger.exception("Renderer release failed")
        super().on_close()
