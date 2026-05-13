from __future__ import annotations

from pathlib import Path

from tvwall.domain import AppConfig, AppState, GRID_OPTIONS, LAYOUT_ORDER
from tvwall.services import ConfigRepository, LayoutService
from tvwall.ui.widgets import PanelAction


class AppController:
    def __init__(self, config_path: Path, repository: ConfigRepository | None = None) -> None:
        self.config_path = config_path
        self.repository = repository or ConfigRepository()
        config = self.repository.load(config_path)
        self.state = AppState(config=config, current_source_index=config.selected_input_index, selected_tv=1)
        LayoutService.normalize_selection(self.state)
        self.state.status_message = "Loaded config"

    def save(self) -> None:
        self.state.config.selected_input_index = self.state.current_source_index
        self.repository.save(self.config_path, self.state.config)
        self.state.status_message = f"Saved {self.config_path.name}"

    def load(self) -> None:
        self.state.config = self.repository.load(self.config_path)
        self.state.current_source_index = self.state.config.selected_input_index
        LayoutService.normalize_selection(self.state)
        self.state.mark_source_dirty()
        self.state.status_message = f"Loaded {self.config_path.name}"

    def handle_action(self, action: PanelAction) -> None:
        payload = action.payload
        if action.command == "save":
            self.save()
        elif action.command == "load":
            self.load()
        elif action.command == "set_source":
            self.set_source(payload["index"])
        elif action.command == "use_testmap":
            self.set_source(2)
        elif action.command == "toggle_hide_map":
            self.state.config.hide_maptest = not self.state.config.hide_maptest
            self.state.mark_config_dirty()
        elif action.command == "toggle_hide_preview":
            self.state.config.hide_preview = not self.state.config.hide_preview
            self.state.mark_config_dirty()
        elif action.command == "toggle_fullscreen":
            self.state.active_monitor.is_fullscreen = not self.state.active_monitor.is_fullscreen
            self.state.mark_config_dirty()
        elif action.command == "toggle_framerate":
            self.state.show_framerate = not self.state.show_framerate
            self.state.mark_config_dirty()
        elif action.command == "adjust_monitor_count":
            LayoutService.adjust_monitor_count(self.state.config, payload["delta"])
            LayoutService.normalize_selection(self.state)
            self.state.mark_config_dirty()
        elif action.command == "set_monitor":
            self.state.config.monitor_selected = payload["index"]
            self.state.config.ensure_lengths()
            LayoutService.normalize_selection(self.state)
            self.state.mark_config_dirty()
        elif action.command == "set_layout":
            LayoutService.set_layout(self.state, LAYOUT_ORDER[payload["index"]])
        elif action.command == "toggle_monitor_focus":
            self.state.config.monitor_focus = not self.state.config.monitor_focus
            LayoutService.normalize_selection(self.state)
            self.state.mark_config_dirty()
        elif action.command == "toggle_output_to_monitor":
            self.state.active_monitor.output_to_monitor = not self.state.active_monitor.output_to_monitor
            self.state.mark_config_dirty()
        elif action.command == "adjust_monitor_field":
            LayoutService.adjust_monitor_field(self.state, payload["field"], payload["delta"])
        elif action.command == "adjust_canvas":
            LayoutService.adjust_canvas_value(self.state, payload["field"], payload["delta"])
        elif action.command == "adjust_tv_count":
            LayoutService.adjust_tv_count(self.state.config, payload["delta"])
            LayoutService.normalize_selection(self.state)
            self.state.mark_source_dirty()
        elif action.command == "select_tv":
            self.select_relative_tv(payload["delta"])
        elif action.command == "set_selected_tv":
            self.state.selected_tv = payload["index"]
            LayoutService.normalize_selection(self.state)
            self.state.mark_config_dirty()
        elif action.command == "set_grid_index":
            self.state.grid_index = payload["index"]
            self.state.mark_config_dirty()
        elif action.command == "adjust_tv_value":
            LayoutService.adjust_tv_value(self.state, payload["index"], payload["field"], payload["delta"])

    def set_source(self, index: int) -> None:
        self.state.current_source_index = max(0, min(index, 2))
        self.state.config.selected_input_index = self.state.current_source_index
        self.state.mark_source_dirty()
        self.state.status_message = "Source changed"

    def select_relative_tv(self, direction: int) -> None:
        visible = LayoutService.visible_tv_indices(self.state)
        if not visible:
            return
        if self.state.selected_tv not in visible:
            self.state.selected_tv = visible[0]
        else:
            current = visible.index(self.state.selected_tv)
            self.state.selected_tv = visible[(current + direction) % len(visible)]
        self.state.status_message = f"Selected TV {self.state.selected_tv}"
        self.state.mark_config_dirty()

    def begin_drag(self, rect, x: float, y: float) -> bool:
        return LayoutService.begin_drag(self.state, rect, x, y)

    def drag_selected(self, rect, x: float, y: float, resize: bool) -> None:
        LayoutService.drag_selected(self.state, rect, x, y, resize)

    def keyboard_move(self, x_direction: int = 0, y_direction: int = 0, resize: bool = False) -> None:
        amount = self.state.grid_size
        if resize:
            LayoutService.resize_selected_tv(self.state, x_direction * amount, y_direction * amount)
        else:
            LayoutService.move_selected_tv(self.state, x_direction * amount, y_direction * amount)

    def cycle_grid(self, direction: int) -> None:
        LayoutService.cycle_grid(self.state, direction)

    def cycle_source(self) -> None:
        self.set_source((self.state.current_source_index + 1) % 3)
