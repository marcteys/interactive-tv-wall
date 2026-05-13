from __future__ import annotations

from tvwall.domain.constants import GRID_OPTIONS, LAYOUT_TO_COUNT, LAYOUT_ORDER
from tvwall.domain.models import AppConfig, AppState, Rect, TVMapping


class LayoutService:
    @staticmethod
    def visible_tv_indices(state: AppState) -> list[int]:
        config = state.config
        if not config.monitor_focus:
            return list(range(1, config.number_tvs + 1))
        start = state.active_monitor.tv_first
        end = min(start + state.active_monitor.tv_number - 1, config.number_tvs)
        return list(range(start, end + 1))

    @staticmethod
    def normalize_selection(state: AppState) -> None:
        visible = LayoutService.visible_tv_indices(state)
        if not visible:
            state.selected_tv = 1
            return
        if state.selected_tv not in visible:
            state.selected_tv = visible[0]
        state.selected_tv = max(1, min(state.selected_tv, state.config.number_tvs))
        state.grid_index = max(0, min(state.grid_index, len(GRID_OPTIONS) - 1))

    @staticmethod
    def set_layout(state: AppState, layout: str) -> None:
        if layout not in LAYOUT_ORDER:
            return
        monitor = state.active_monitor
        monitor.tv_layout = layout
        monitor.tv_number = min(LAYOUT_TO_COUNT[layout], state.config.number_tvs)
        monitor.tv_first = max(1, min(monitor.tv_first, state.config.number_tvs))
        state.status_message = f"Layout changed to {layout}"
        state.mark_config_dirty()
        LayoutService.normalize_selection(state)

    @staticmethod
    def adjust_tv_count(config: AppConfig, delta: int) -> None:
        config.number_tvs = max(1, config.number_tvs + delta)
        config.ensure_lengths()
        for monitor in config.monitor_data:
            monitor.tv_first = max(1, min(monitor.tv_first, config.number_tvs))
            monitor.tv_number = max(1, min(monitor.tv_number, config.number_tvs))

    @staticmethod
    def adjust_monitor_count(config: AppConfig, delta: int) -> None:
        config.number_monitors = max(1, config.number_monitors + delta)
        config.ensure_lengths()

    @staticmethod
    def adjust_monitor_field(state: AppState, field_name: str, delta: int) -> None:
        monitor = state.active_monitor
        if not hasattr(monitor, field_name):
            return
        setattr(monitor, field_name, getattr(monitor, field_name) + delta)
        state.config.ensure_lengths()
        LayoutService.normalize_selection(state)
        state.mark_config_dirty()

    @staticmethod
    def adjust_canvas_value(state: AppState, field_name: str, delta: int) -> None:
        if not hasattr(state.config, field_name):
            return
        setattr(state.config, field_name, max(1, getattr(state.config, field_name) + delta))
        state.mark_source_dirty()

    @staticmethod
    def adjust_tv_value(state: AppState, tv_index: int, field_name: str, delta: int) -> None:
        tv = state.config.tv_mappings[tv_index - 1]
        if not hasattr(tv, field_name):
            return
        setattr(tv, field_name, getattr(tv, field_name) + delta)
        state.mark_source_dirty()

    @staticmethod
    def move_selected_tv(state: AppState, dx: int, dy: int) -> None:
        tv = state.config.tv_mappings[state.selected_tv - 1]
        tv.x_pos += dx
        tv.y_pos += dy
        state.status_message = f"Moved TV {state.selected_tv}"
        state.mark_source_dirty()

    @staticmethod
    def resize_selected_tv(state: AppState, dw: int, dh: int) -> None:
        tv = state.config.tv_mappings[state.selected_tv - 1]
        tv.width += dw
        tv.height += dh
        state.status_message = f"Resized TV {state.selected_tv}"
        state.mark_source_dirty()

    @staticmethod
    def select_relative_tv(state: AppState, direction: int) -> None:
        visible = LayoutService.visible_tv_indices(state)
        if not visible:
            return
        current = visible.index(state.selected_tv) if state.selected_tv in visible else 0
        state.selected_tv = visible[(current + direction) % len(visible)]
        state.status_message = f"Selected TV {state.selected_tv}"
        state.mark_config_dirty()

    @staticmethod
    def cycle_grid(state: AppState, direction: int) -> None:
        state.grid_index = (state.grid_index + direction) % len(GRID_OPTIONS)
        state.status_message = f"Grid changed to {state.grid_size} mm"
        state.mark_config_dirty()

    @staticmethod
    def screen_to_canvas(rect: Rect, x: float, y: float, config: AppConfig) -> tuple[float, float] | None:
        if not rect.contains(x, y):
            return None
        local_x = (x - rect.x) / max(rect.width, 1) * config.canvas_width
        local_y = (y - rect.y) / max(rect.height, 1) * config.canvas_height
        return local_x, local_y

    @staticmethod
    def hit_test(state: AppState, rect: Rect, x: float, y: float) -> int | None:
        point = LayoutService.screen_to_canvas(rect, x, y, state.config)
        if point is None:
            return None
        px, py = point
        for tv_index in reversed(LayoutService.visible_tv_indices(state)):
            tv = state.config.tv_mappings[tv_index - 1]
            x_min, x_max = sorted((tv.x_pos, tv.x_pos + tv.width))
            y_min, y_max = sorted((tv.y_pos, tv.y_pos + tv.height))
            if x_min <= px <= x_max and y_min <= py <= y_max:
                return tv_index
        return None

    @staticmethod
    def begin_drag(state: AppState, rect: Rect, x: float, y: float) -> bool:
        hit = LayoutService.hit_test(state, rect, x, y)
        if hit is None:
            state.status_message = "Clicked outside any TV region"
            return False
        point = LayoutService.screen_to_canvas(rect, x, y, state.config)
        if point is None:
            return False
        px, py = point
        state.selected_tv = hit
        tv = state.config.tv_mappings[hit - 1]
        state.drag_offset_x = px - tv.x_pos
        state.drag_offset_y = py - tv.y_pos
        state.status_message = f"Selected TV {hit}"
        state.mark_config_dirty()
        return True

    @staticmethod
    def drag_selected(state: AppState, rect: Rect, x: float, y: float, resize: bool) -> None:
        if state.selected_tv < 1 or state.selected_tv > state.config.number_tvs:
            return
        point = LayoutService.screen_to_canvas(rect, x, y, state.config)
        if point is None:
            return
        px, py = point
        tv = state.config.tv_mappings[state.selected_tv - 1]
        if resize:
            tv.width = int(px - tv.x_pos)
            tv.height = int(py - tv.y_pos)
            state.status_message = f"Resized TV {state.selected_tv}"
        else:
            tv.x_pos = int(px - state.drag_offset_x)
            tv.y_pos = int(py - state.drag_offset_y)
            state.status_message = f"Moved TV {state.selected_tv}"
        state.mark_source_dirty()

    @staticmethod
    def pack_tv_uniforms(mappings: list[TVMapping], start_index: int, count: int, max_count: int = 9) -> tuple[bytes, int]:
        packed = bytearray()
        safe_count = max(1, min(count, max_count))
        for offset in range(max_count):
            index = min(start_index + offset, len(mappings) - 1)
            tv = mappings[index]
            for value in (tv.width, tv.height, tv.x_pos, tv.y_pos):
                packed.extend(int(value).to_bytes(4, "little", signed=True))
        return bytes(packed), safe_count
