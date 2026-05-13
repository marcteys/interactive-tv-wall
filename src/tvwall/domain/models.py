from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import List

from .constants import GRID_OPTIONS, LAYOUT_TO_COUNT, LAYOUT_ORDER, SOURCE_LABELS


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    width: float
    height: float

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def top(self) -> float:
        return self.y + self.height

    def contains(self, px: float, py: float) -> bool:
        return self.x <= px <= self.right and self.y <= py <= self.top


@dataclass
class TVMapping:
    width: int = 1000
    height: int = 1000
    x_pos: int = 0
    y_pos: int = 0


@dataclass
class MonitorConfig:
    output_to_monitor: bool = True
    output_to_ndi: bool = False
    is_fullscreen: bool = False
    display_index: int = 0
    tv_number: int = 1
    tv_first: int = 1
    tv_layout: str = "1"


@dataclass
class AppConfig:
    hide_maptest: bool = False
    hide_preview: bool = False
    set_resolutions: bool = False
    input_width: int = 1920
    input_height: int = 1080
    framerate: int = 30
    number_tvs: int = 1
    selected_input_index: int = 0
    canvas_width: int = 5000
    canvas_height: int = 5000
    number_monitors: int = 1
    monitor_selected: int = 0
    monitor_focus: bool = False
    monitor_data: List[MonitorConfig] = field(default_factory=lambda: [MonitorConfig()])
    tv_mappings: List[TVMapping] = field(default_factory=lambda: [TVMapping()])

    @classmethod
    def default_monitor(cls) -> MonitorConfig:
        return MonitorConfig()

    def ensure_lengths(self) -> None:
        self.input_width = max(64, int(self.input_width))
        self.input_height = max(64, int(self.input_height))
        self.framerate = max(1, int(self.framerate))
        self.canvas_width = max(1, int(self.canvas_width))
        self.canvas_height = max(1, int(self.canvas_height))
        self.number_tvs = max(1, int(self.number_tvs))
        self.selected_input_index = max(0, min(int(self.selected_input_index), len(SOURCE_LABELS) - 1))

        while len(self.tv_mappings) < self.number_tvs:
            self.tv_mappings.append(TVMapping())
        if len(self.tv_mappings) > self.number_tvs:
            self.tv_mappings = self.tv_mappings[: self.number_tvs]

        if not self.monitor_data:
            self.monitor_data = [self.default_monitor()]
        self.number_monitors = max(1, int(self.number_monitors), len(self.monitor_data))
        while len(self.monitor_data) < self.number_monitors:
            self.monitor_data.append(self.default_monitor())
        if len(self.monitor_data) > self.number_monitors:
            self.monitor_data = self.monitor_data[: self.number_monitors]

        self.monitor_selected = max(0, min(int(self.monitor_selected), self.number_monitors - 1))

        for monitor in self.monitor_data:
            if monitor.tv_layout not in LAYOUT_ORDER:
                monitor.tv_layout = "1"
            monitor.tv_number = max(1, min(int(monitor.tv_number), LAYOUT_TO_COUNT[monitor.tv_layout]))
            monitor.tv_first = max(1, min(int(monitor.tv_first), self.number_tvs))

    def to_json(self) -> dict:
        self.ensure_lengths()
        return {
            "hide_maptest": self.hide_maptest,
            "hide_preview": self.hide_preview,
            "set_resolutions": self.set_resolutions,
            "input_width": self.input_width,
            "input_height": self.input_height,
            "framerate": self.framerate,
            "number_tvs": self.number_tvs,
            "selected_input_index": self.selected_input_index,
            "canvas_width": self.canvas_width,
            "canvas_height": self.canvas_height,
            "number_monitors": self.number_monitors,
            "monitor_selected": self.monitor_selected,
            "monitor_focus": self.monitor_focus,
            "monitor_data": [asdict(item) for item in self.monitor_data],
            "tv_mappings": [asdict(item) for item in self.tv_mappings],
        }


@dataclass
class AppState:
    config: AppConfig
    current_source_index: int = 0
    selected_tv: int = 1
    grid_index: int = 0
    show_framerate: bool = False
    status_message: str = "Ready"
    panel_scroll: float = 0.0
    drag_offset_x: float = 0.0
    drag_offset_y: float = 0.0
    source_revision: int = 0
    config_revision: int = 0

    @property
    def active_monitor(self) -> MonitorConfig:
        self.config.ensure_lengths()
        return self.config.monitor_data[self.config.monitor_selected]

    @property
    def grid_size(self) -> int:
        return GRID_OPTIONS[self.grid_index]

    def mark_source_dirty(self) -> None:
        self.source_revision += 1
        self.config_revision += 1

    def mark_config_dirty(self) -> None:
        self.config_revision += 1

