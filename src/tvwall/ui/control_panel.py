from __future__ import annotations

from tvwall.domain import GRID_OPTIONS, LAYOUT_ORDER, SOURCE_LABELS
from tvwall.domain.models import AppState, Rect
from pyglet.window import key
from tvwall.ui.widgets import PanelAction, WidgetPainter


class ControlPanelView:
    def __init__(self) -> None:
        self.painter = WidgetPainter()
        self.scroll_offset = 0.0
        self.max_scroll = 0.0
        self.scroll_rect = Rect(0, 0, 0, 0)
        self.scrollbar_track_rect = Rect(0, 0, 0, 0)
        self.scrollbar_thumb_rect = Rect(0, 0, 0, 0)
        self._scroll_drag_active = False
        self._scroll_drag_offset = 0.0
        self.section_expanded = {
            "mode_source": True,
            "monitor_settings": True,
            "canvas_map": True,
            "tv_values": True,
        }
        self.active_value_edit: dict | None = None

    def hit_test(self, x: float, y: float) -> PanelAction | None:
        # Regions are populated by draw(); returns None if draw() hasn't run yet this frame.
        if not self.scroll_rect.contains(x, y):
            self.cancel_value_edit()
            return None
        action = self.painter.hit_test(x, y)
        if action and action.command == "edit_value":
            self.active_value_edit = {
                "action": action.payload["commit_action"],
                "buffer": action.payload["current_value"],
            }
            return PanelAction("noop")
        if action is not None and self.active_value_edit is not None:
            self.cancel_value_edit()
        if action and action.command == "toggle_section":
            section = action.payload["section"]
            self.section_expanded[section] = not self.section_expanded.get(section, True)
            return PanelAction("noop")
        return action

    def tooltip_at(self, x: float, y: float) -> str | None:
        if not self.scroll_rect.contains(x, y):
            return None
        return self.painter.tooltip_at(x, y)

    def scroll(self, amount: float) -> None:
        self.scroll_offset = max(0.0, min(self.scroll_offset + amount, self.max_scroll))

    def cancel_value_edit(self) -> None:
        self.active_value_edit = None

    def handle_text(self, text: str) -> bool:
        if self.active_value_edit is None:
            return False
        if text.isdigit():
            self.active_value_edit["buffer"] += text
            return True
        if text == "-" and not self.active_value_edit["buffer"]:
            self.active_value_edit["buffer"] = "-"
            return True
        return False

    def handle_key_press(self, symbol: int) -> PanelAction | None:
        if self.active_value_edit is None:
            return None
        if symbol in (key.ENTER, key.NUM_ENTER):
            return self.commit_value_edit()
        if symbol == key.ESCAPE:
            self.cancel_value_edit()
            return PanelAction("noop")
        if symbol == key.BACKSPACE:
            self.active_value_edit["buffer"] = self.active_value_edit["buffer"][:-1]
            return PanelAction("noop")
        return PanelAction("noop")

    def commit_value_edit(self) -> PanelAction:
        assert self.active_value_edit is not None
        buffer = self.active_value_edit["buffer"].strip()
        commit_action = self.active_value_edit["action"]
        self.active_value_edit = None
        if buffer in {"", "-"}:
            return PanelAction("noop")
        payload = dict(commit_action.payload)
        payload["value"] = int(buffer)
        return PanelAction(commit_action.command, payload)

    def begin_scroll_drag(self, x: float, y: float) -> bool:
        if self.max_scroll <= 0:
            return False
        if self.scrollbar_thumb_rect.contains(x, y):
            self._scroll_drag_active = True
            self._scroll_drag_offset = y - self.scrollbar_thumb_rect.y
            return True
        if self.scrollbar_track_rect.contains(x, y):
            thumb_center = self.scrollbar_thumb_rect.y + self.scrollbar_thumb_rect.height / 2
            page = max(48.0, self.scroll_rect.height * 0.8)
            direction = 1 if y > thumb_center else -1
            self.scroll(direction * page)
            return True
        return False

    def drag_scrollbar(self, y: float) -> bool:
        if not self._scroll_drag_active or self.max_scroll <= 0:
            return False
        travel = max(0.0, self.scrollbar_track_rect.height - self.scrollbar_thumb_rect.height)
        if travel <= 0:
            return False
        thumb_y = min(
            max(self.scrollbar_track_rect.y, y - self._scroll_drag_offset),
            self.scrollbar_track_rect.y + travel,
        )
        ratio = (thumb_y - self.scrollbar_track_rect.y) / travel
        self.scroll_offset = ratio * self.max_scroll
        return True

    def end_scroll_drag(self) -> None:
        self._scroll_drag_active = False
        self._scroll_drag_offset = 0.0

    def draw(self, state: AppState, rect: Rect) -> None:
        self.painter.reset()
        self.painter.panel(rect)
        self.scroll_rect = Rect(rect.x + 8, rect.y + 8, rect.width - 16, rect.height - 16)
        self.painter.set_clip_rect(self.scroll_rect)
        x = rect.x + 16
        y = rect.top - 30 + self.scroll_offset
        self.painter.section_title(x, y, "TV WALL MAPPER")
        y -= 34
        self.painter.body_text(
            x,
            y,
            "Mouse-first editing: use the panel to adjust monitor, canvas, and TV values. Drag TVs in the map preview to move or resize them.",
            width=int(rect.width - 32),
        )
        y -= 92

        y = self._draw_mode_source_section(state, rect, x, y)
        y = self._draw_monitor_section(state, rect, x, y)
        y = self._draw_canvas_section(state, rect, x, y)
        y = self._draw_tv_values_section(state, rect, x, y)
        content_bottom = y - self.scroll_offset
        content_height = (rect.top - 30) - content_bottom
        self.max_scroll = max(0.0, content_height - self.scroll_rect.height + 24)
        self.scroll_offset = max(0.0, min(self.scroll_offset, self.max_scroll))
        self._draw_scrollbar()
        self.painter.finish()

    def _section_header(self, x: float, y: float, width: float, title: str, key: str, subtitle: str) -> float:
        self.painter.section_header(
            Rect(x, y - 34, width, 38),
            title,
            self.section_expanded.get(key, True),
            PanelAction("toggle_section", {"section": key}),
            subtitle=subtitle,
        )
        return y - 50

    def _section_card(self, x: float, y_top: float, width: float, height: float) -> None:
        self.painter.surface(Rect(x, y_top - height, width, height), (28, 29, 36), (62, 66, 82))

    def _value_text(self, action: PanelAction, fallback: str) -> str:
        if self.active_value_edit and self.active_value_edit["action"] == action:
            return self.active_value_edit["buffer"] or "|"
        return fallback

    def _value_active(self, action: PanelAction) -> bool:
        return bool(self.active_value_edit and self.active_value_edit["action"] == action)

    @staticmethod
    def _edit_action(commit_action: PanelAction, current_value: str) -> PanelAction:
        return PanelAction("edit_value", {"commit_action": commit_action, "current_value": current_value})

    def _draw_mode_source_section(self, state: AppState, rect: Rect, x: float, y: float) -> float:
        width = rect.width - 32
        y = self._section_header(x, y, width, "Mode / Source", "mode_source", "Source and runtime toggles")
        if not self.section_expanded["mode_source"]:
            return y - 12
        content_top = y
        content_bottom = y - 120
        self._section_card(x - 8, content_top + 6, width + 16, content_top - content_bottom + 18)
        self.painter.segmented(
            x, y - 28, width, 28, list(SOURCE_LABELS), state.current_source_index, "set_source",
            tooltips=[
                "Use the first testcard image as the video source.",
                "Use the grid testcard image as the video source.",
                "Use the generated map preview as the video source.",
            ],
        )
        y -= 70
        self.painter.toggle(Rect(x, y, 164, 26), "Hide Map", state.config.hide_maptest, PanelAction("toggle_hide_map"), tooltip="Show or hide the mapping preview on the right.")
        self.painter.toggle(Rect(x + 176, y, 164, 26), "Hide Preview", state.config.hide_preview, PanelAction("toggle_hide_preview"), tooltip="Show or hide the shader output preview.")
        y -= 38
        self.painter.toggle(Rect(x, y, 164, 26), "Fullscreen", state.active_monitor.is_fullscreen, PanelAction("toggle_fullscreen"), tooltip="Toggle fullscreen for the main application window.")
        self.painter.toggle(Rect(x + 176, y, 164, 26), "Framerate", state.show_framerate, PanelAction("toggle_framerate"), tooltip="Show or hide the live FPS overlay.")
        y -= 38
        self.painter.button(Rect(x, y, 100, 28), "Save", PanelAction("save"), tooltip="Write the current mapping to config.json.")
        self.painter.button(Rect(x + 112, y, 100, 28), "Load", PanelAction("load"), tooltip="Reload config.json from disk.")
        self.painter.button(Rect(x + 224, y, 116, 28), "Use Testmap", PanelAction("use_testmap"), tooltip="Switch the source to the generated map view for alignment work.")
        return content_bottom - 24

    def _draw_monitor_section(self, state: AppState, rect: Rect, x: float, y: float) -> float:
        width = rect.width - 32
        y = self._section_header(x, y, width, "Monitor Settings", "monitor_settings", "Per-output assignment and layout")
        if not self.section_expanded["monitor_settings"]:
            return y - 12
        content_top = y
        content_bottom = y - 168
        self._section_card(x - 8, content_top + 6, width + 16, content_top - content_bottom + 18)
        commit_action = PanelAction("set_monitor_count")
        self.painter.stepper(x, y - 22, width, "Monitor Count", self._value_text(commit_action, str(state.config.number_monitors)), PanelAction("adjust_monitor_count", {"delta": -1}), PanelAction("adjust_monitor_count", {"delta": 1}), value_action=self._edit_action(commit_action, str(state.config.number_monitors)), value_active=self._value_active(commit_action), tooltip="Set how many monitor configurations exist in the project.")
        y -= 68
        self.painter.segmented(x, y, width, 28, [f"M{index + 1}" for index in range(state.config.number_monitors)], state.config.monitor_selected, "set_monitor", tooltips=[f"Edit settings for monitor slot {index + 1}." for index in range(state.config.number_monitors)])
        y -= 40
        layout_index = list(LAYOUT_ORDER).index(state.active_monitor.tv_layout)
        self.painter.segmented(
            x, y, width, 28, list(LAYOUT_ORDER), layout_index, "set_layout",
            tooltips=[
                "Single-output layout: map one TV feed to this monitor.",
                "2 by 2 wall layout: split output for a 4-screen wall processor.",
                "3 by 3 wall layout: split output for a 9-screen wall processor.",
            ],
        )
        y -= 40
        self.painter.toggle(Rect(x, y, 164, 26), "Monitor Focus", state.config.monitor_focus, PanelAction("toggle_monitor_focus"), tooltip="Only show TVs assigned to the active monitor in the map preview.")
        self.painter.toggle(Rect(x + 176, y, 164, 26), "Output Enabled", state.active_monitor.output_to_monitor, PanelAction("toggle_output_to_monitor"), tooltip="Keep this monitor configuration active in the preview/output flow.")
        y -= 38
        commit_action = PanelAction("set_monitor_field", {"field": "tv_number"})
        self.painter.stepper(x, y, width, "TVs On Output", self._value_text(commit_action, str(state.active_monitor.tv_number)), PanelAction("adjust_monitor_field", {"field": "tv_number", "delta": -1}), PanelAction("adjust_monitor_field", {"field": "tv_number", "delta": 1}), value_action=self._edit_action(commit_action, str(state.active_monitor.tv_number)), value_active=self._value_active(commit_action), tooltip="Choose how many TVs from the global mapping feed this monitor output.")
        y -= 46
        commit_action = PanelAction("set_monitor_field", {"field": "tv_first"})
        self.painter.stepper(x, y, width, "First TV", self._value_text(commit_action, str(state.active_monitor.tv_first)), PanelAction("adjust_monitor_field", {"field": "tv_first", "delta": -1}), PanelAction("adjust_monitor_field", {"field": "tv_first", "delta": 1}), value_action=self._edit_action(commit_action, str(state.active_monitor.tv_first)), value_active=self._value_active(commit_action), tooltip="Choose the first TV index assigned to this monitor output.")
        return content_bottom - 24

    def _draw_canvas_section(self, state: AppState, rect: Rect, x: float, y: float) -> float:
        width = rect.width - 32
        y = self._section_header(x, y, width, "Canvas / Map", "canvas_map", "Wall dimensions and edit step size")
        if not self.section_expanded["canvas_map"]:
            return y - 12
        content_top = y
        content_bottom = y - 154
        self._section_card(x - 8, content_top + 6, width + 16, content_top - content_bottom + 18)
        commit_action = PanelAction("set_canvas_value", {"field": "canvas_width"})
        self.painter.stepper(x, y - 22, width, "Canvas Width", self._value_text(commit_action, str(state.config.canvas_width)), PanelAction("adjust_canvas", {"field": "canvas_width", "delta": -100}), PanelAction("adjust_canvas", {"field": "canvas_width", "delta": 100}), value_action=self._edit_action(commit_action, str(state.config.canvas_width)), value_active=self._value_active(commit_action), tooltip="Physical width of the full mapped wall, in millimeters.")
        y -= 68
        commit_action = PanelAction("set_canvas_value", {"field": "canvas_height"})
        self.painter.stepper(x, y, width, "Canvas Height", self._value_text(commit_action, str(state.config.canvas_height)), PanelAction("adjust_canvas", {"field": "canvas_height", "delta": -100}), PanelAction("adjust_canvas", {"field": "canvas_height", "delta": 100}), value_action=self._edit_action(commit_action, str(state.config.canvas_height)), value_active=self._value_active(commit_action), tooltip="Physical height of the full mapped wall, in millimeters.")
        y -= 46
        commit_action = PanelAction("set_tv_count")
        self.painter.stepper(x, y, width, "TV Count", self._value_text(commit_action, str(state.config.number_tvs)), PanelAction("adjust_tv_count", {"delta": -1}), PanelAction("adjust_tv_count", {"delta": 1}), value_action=self._edit_action(commit_action, str(state.config.number_tvs)), value_active=self._value_active(commit_action), tooltip="Total number of TVs in the installation mapping.")
        y -= 46
        commit_action = PanelAction("set_selected_tv_value")
        self.painter.stepper(x, y, width, "Selected TV", self._value_text(commit_action, str(state.selected_tv)), PanelAction("select_tv", {"delta": -1}), PanelAction("select_tv", {"delta": 1}), value_action=self._edit_action(commit_action, str(state.selected_tv)), value_active=self._value_active(commit_action), tooltip="Choose which TV is currently selected for keyboard and field edits.")
        y -= 40
        self.painter.segmented(x, y, width, 28, [str(value) for value in GRID_OPTIONS], state.grid_index, "set_grid_index", tooltips=[f"Move and resize in {value} mm steps." for value in GRID_OPTIONS])
        return content_bottom - 24

    def _draw_tv_values_section(self, state: AppState, rect: Rect, x: float, y: float) -> float:
        width = rect.width - 32
        y = self._section_header(x, y, width, "TV Values", "tv_values", "Per-screen geometry and positions")
        if not self.section_expanded["tv_values"]:
            return y - 12
        content_top = y
        content_bottom = y - (len(state.config.tv_mappings) * 148) - 8
        self._section_card(x - 8, content_top + 6, width + 16, content_top - content_bottom + 18)
        y -= 18
        for tv_index, tv in enumerate(state.config.tv_mappings, start=1):
            self.painter.button(Rect(x, y, 80, 24), f"TV {tv_index}", PanelAction("set_selected_tv", {"index": tv_index}), active=tv_index == state.selected_tv, tooltip=f"Select TV {tv_index} for editing and keyboard nudging.")
            commit_action = PanelAction("set_tv_value", {"index": tv_index, "field": "width"})
            self.painter.stepper(x + 92, y, rect.width - 124, "Width", self._value_text(commit_action, str(tv.width)), PanelAction("adjust_tv_value", {"index": tv_index, "field": "width", "delta": -10}), PanelAction("adjust_tv_value", {"index": tv_index, "field": "width", "delta": 10}), value_action=self._edit_action(commit_action, str(tv.width)), value_active=self._value_active(commit_action), tooltip=f"Physical width of TV {tv_index}, in millimeters.")
            y -= 34
            commit_action = PanelAction("set_tv_value", {"index": tv_index, "field": "height"})
            self.painter.stepper(x + 92, y, rect.width - 124, "Height", self._value_text(commit_action, str(tv.height)), PanelAction("adjust_tv_value", {"index": tv_index, "field": "height", "delta": -10}), PanelAction("adjust_tv_value", {"index": tv_index, "field": "height", "delta": 10}), value_action=self._edit_action(commit_action, str(tv.height)), value_active=self._value_active(commit_action), tooltip=f"Physical height of TV {tv_index}, in millimeters.")
            y -= 34
            commit_action = PanelAction("set_tv_value", {"index": tv_index, "field": "x_pos"})
            self.painter.stepper(x + 92, y, rect.width - 124, "X", self._value_text(commit_action, str(tv.x_pos)), PanelAction("adjust_tv_value", {"index": tv_index, "field": "x_pos", "delta": -10}), PanelAction("adjust_tv_value", {"index": tv_index, "field": "x_pos", "delta": 10}), value_action=self._edit_action(commit_action, str(tv.x_pos)), value_active=self._value_active(commit_action), tooltip=f"Horizontal position of TV {tv_index} on the full wall, in millimeters.")
            y -= 34
            commit_action = PanelAction("set_tv_value", {"index": tv_index, "field": "y_pos"})
            self.painter.stepper(x + 92, y, rect.width - 124, "Y", self._value_text(commit_action, str(tv.y_pos)), PanelAction("adjust_tv_value", {"index": tv_index, "field": "y_pos", "delta": -10}), PanelAction("adjust_tv_value", {"index": tv_index, "field": "y_pos", "delta": 10}), value_action=self._edit_action(commit_action, str(tv.y_pos)), value_active=self._value_active(commit_action), tooltip=f"Vertical position of TV {tv_index} on the full wall, in millimeters.")
            y -= 46
        return content_bottom - 24

    def _draw_scrollbar(self) -> None:
        self.scrollbar_track_rect = Rect(0, 0, 0, 0)
        self.scrollbar_thumb_rect = Rect(0, 0, 0, 0)
        if self.max_scroll <= 0 or self.scroll_rect.height <= 0:
            return
        track_width = 8
        track = Rect(self.scroll_rect.right - track_width, self.scroll_rect.y, track_width, self.scroll_rect.height)
        self.scrollbar_track_rect = track
        self.painter.surface(track, (34, 34, 40), (68, 68, 80))
        thumb_height = max(36.0, self.scroll_rect.height * (self.scroll_rect.height / (self.scroll_rect.height + self.max_scroll)))
        travel = max(0.0, track.height - thumb_height)
        thumb_y = track.y + travel * (self.scroll_offset / self.max_scroll)
        self.scrollbar_thumb_rect = Rect(track.x, thumb_y, track.width, thumb_height)
        self.painter.surface(self.scrollbar_thumb_rect, (72, 92, 170), (106, 130, 240))
