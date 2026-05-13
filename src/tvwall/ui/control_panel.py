from __future__ import annotations

from tvwall.domain import GRID_OPTIONS, LAYOUT_ORDER, SOURCE_LABELS
from tvwall.domain.models import AppState, Rect
from tvwall.ui.widgets import PanelAction, WidgetPainter


class ControlPanelView:
    def __init__(self) -> None:
        self.painter = WidgetPainter()
        self.scroll_offset = 0.0

    def hit_test(self, x: float, y: float) -> PanelAction | None:
        return self.painter.hit_test(x, y)

    def scroll(self, amount: float) -> None:
        self.scroll_offset = max(0.0, self.scroll_offset + amount)

    def draw(self, state: AppState, rect: Rect) -> None:
        self.painter.reset()
        self.painter.panel(rect)
        x = rect.x + 16
        y = rect.top - 30
        self.painter.section_title(x, y, "TV WALL MAPPER")
        y -= 34
        self.painter.body_text(
            x,
            y,
            "Mouse-first editing: use the panel to adjust monitor, canvas, and TV values. Drag TVs in the map preview to move or resize them.",
            width=int(rect.width - 32),
        )
        y -= 92

        self.painter.section_title(x, y, "Mode / Source")
        y -= 34
        self.painter.segmented(x, y, rect.width - 32, 28, list(SOURCE_LABELS), state.current_source_index, "set_source")
        y -= 42
        self.painter.toggle(Rect(x, y, 164, 26), "Hide Map", state.config.hide_maptest, PanelAction("toggle_hide_map"))
        self.painter.toggle(Rect(x + 176, y, 164, 26), "Hide Preview", state.config.hide_preview, PanelAction("toggle_hide_preview"))
        y -= 38
        self.painter.toggle(Rect(x, y, 164, 26), "Fullscreen", state.active_monitor.is_fullscreen, PanelAction("toggle_fullscreen"))
        self.painter.toggle(Rect(x + 176, y, 164, 26), "Framerate", state.show_framerate, PanelAction("toggle_framerate"))
        y -= 38
        self.painter.button(Rect(x, y, 100, 28), "Save", PanelAction("save"))
        self.painter.button(Rect(x + 112, y, 100, 28), "Load", PanelAction("load"))
        self.painter.button(Rect(x + 224, y, 116, 28), "Use Testmap", PanelAction("use_testmap"))
        y -= 48

        self.painter.section_title(x, y, "Monitor Settings")
        y -= 34
        self.painter.stepper(
            x, y, rect.width - 32, "Monitor Count", str(state.config.number_monitors),
            PanelAction("adjust_monitor_count", {"delta": -1}),
            PanelAction("adjust_monitor_count", {"delta": 1}),
        )
        y -= 46
        self.painter.segmented(
            x, y, rect.width - 32, 28,
            [f"M{index + 1}" for index in range(state.config.number_monitors)],
            state.config.monitor_selected,
            "set_monitor",
        )
        y -= 40
        layout_index = list(LAYOUT_ORDER).index(state.active_monitor.tv_layout)
        self.painter.segmented(x, y, rect.width - 32, 28, list(LAYOUT_ORDER), layout_index, "set_layout")
        y -= 40
        self.painter.toggle(Rect(x, y, 164, 26), "Monitor Focus", state.config.monitor_focus, PanelAction("toggle_monitor_focus"))
        self.painter.toggle(Rect(x + 176, y, 164, 26), "Output Enabled", state.active_monitor.output_to_monitor, PanelAction("toggle_output_to_monitor"))
        y -= 38
        self.painter.stepper(
            x, y, rect.width - 32, "TVs On Output", str(state.active_monitor.tv_number),
            PanelAction("adjust_monitor_field", {"field": "tv_number", "delta": -1}),
            PanelAction("adjust_monitor_field", {"field": "tv_number", "delta": 1}),
        )
        y -= 46
        self.painter.stepper(
            x, y, rect.width - 32, "First TV", str(state.active_monitor.tv_first),
            PanelAction("adjust_monitor_field", {"field": "tv_first", "delta": -1}),
            PanelAction("adjust_monitor_field", {"field": "tv_first", "delta": 1}),
        )
        y -= 48

        self.painter.section_title(x, y, "Canvas / Map")
        y -= 34
        self.painter.stepper(
            x, y, rect.width - 32, "Canvas Width", str(state.config.canvas_width),
            PanelAction("adjust_canvas", {"field": "canvas_width", "delta": -100}),
            PanelAction("adjust_canvas", {"field": "canvas_width", "delta": 100}),
        )
        y -= 46
        self.painter.stepper(
            x, y, rect.width - 32, "Canvas Height", str(state.config.canvas_height),
            PanelAction("adjust_canvas", {"field": "canvas_height", "delta": -100}),
            PanelAction("adjust_canvas", {"field": "canvas_height", "delta": 100}),
        )
        y -= 46
        self.painter.stepper(
            x, y, rect.width - 32, "TV Count", str(state.config.number_tvs),
            PanelAction("adjust_tv_count", {"delta": -1}),
            PanelAction("adjust_tv_count", {"delta": 1}),
        )
        y -= 46
        self.painter.stepper(
            x, y, rect.width - 32, "Selected TV", str(state.selected_tv),
            PanelAction("select_tv", {"delta": -1}),
            PanelAction("select_tv", {"delta": 1}),
        )
        y -= 40
        self.painter.segmented(
            x,
            y,
            rect.width - 32,
            28,
            [str(value) for value in GRID_OPTIONS],
            state.grid_index,
            "set_grid_index",
        )
        y -= 52

        self.painter.section_title(x, y, "TV Values")
        y -= 30
        tv_y = y - self.scroll_offset
        for tv_index, tv in enumerate(state.config.tv_mappings, start=1):
            if tv_y < rect.y + 24:
                tv_y -= 134
                continue
            self.painter.button(
                Rect(x, tv_y, 80, 24),
                f"TV {tv_index}",
                PanelAction("set_selected_tv", {"index": tv_index}),
                active=tv_index == state.selected_tv,
            )
            self.painter.stepper(
                x + 92, tv_y, rect.width - 124, "Width", str(tv.width),
                PanelAction("adjust_tv_value", {"index": tv_index, "field": "width", "delta": -10}),
                PanelAction("adjust_tv_value", {"index": tv_index, "field": "width", "delta": 10}),
            )
            tv_y -= 34
            self.painter.stepper(
                x + 92, tv_y, rect.width - 124, "Height", str(tv.height),
                PanelAction("adjust_tv_value", {"index": tv_index, "field": "height", "delta": -10}),
                PanelAction("adjust_tv_value", {"index": tv_index, "field": "height", "delta": 10}),
            )
            tv_y -= 34
            self.painter.stepper(
                x + 92, tv_y, rect.width - 124, "X", str(tv.x_pos),
                PanelAction("adjust_tv_value", {"index": tv_index, "field": "x_pos", "delta": -10}),
                PanelAction("adjust_tv_value", {"index": tv_index, "field": "x_pos", "delta": 10}),
            )
            tv_y -= 34
            self.painter.stepper(
                x + 92, tv_y, rect.width - 124, "Y", str(tv.y_pos),
                PanelAction("adjust_tv_value", {"index": tv_index, "field": "y_pos", "delta": -10}),
                PanelAction("adjust_tv_value", {"index": tv_index, "field": "y_pos", "delta": 10}),
            )
            tv_y -= 46
