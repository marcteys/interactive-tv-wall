from __future__ import annotations

import json
import os
from pathlib import Path

from tvwall.domain.models import AppConfig, MonitorConfig, TVMapping


class ConfigRepository:
    def load(self, path: Path) -> AppConfig:
        if not path.exists():
            config = AppConfig()
            config.ensure_lengths()
            return config

        data = json.loads(path.read_text(encoding="utf-8"))
        config = AppConfig(
            hide_maptest=data.get("hide_maptest", False),
            hide_preview=data.get("hide_preview", False),
            set_resolutions=data.get("set_resolutions", False),
            input_width=data.get("input_width", 1920),
            input_height=data.get("input_height", 1080),
            framerate=data.get("framerate", 30),
            number_tvs=data.get("number_tvs", 1),
            selected_input_index=data.get("selected_input_index", 0),
            canvas_width=data.get("canvas_width", 5000),
            canvas_height=data.get("canvas_height", 5000),
            number_monitors=data.get("number_monitors", 1),
            monitor_selected=data.get("monitor_selected", 0),
            monitor_focus=data.get("monitor_focus", False),
            monitor_data=[MonitorConfig(**item) for item in data.get("monitor_data", [])] or [MonitorConfig()],
            tv_mappings=[TVMapping(**item) for item in data.get("tv_mappings", [])] or [TVMapping()],
        )
        config.ensure_lengths()
        return config

    def save(self, path: Path, config: AppConfig) -> None:
        config.ensure_lengths()
        payload = json.dumps(config.to_json(), indent=2)
        temp_path = path.with_suffix(path.suffix + ".tmp")
        temp_path.write_text(payload, encoding="utf-8")
        os.replace(temp_path, path)
