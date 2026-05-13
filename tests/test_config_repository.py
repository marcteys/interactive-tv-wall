from __future__ import annotations

from pathlib import Path

from tvwall.domain.models import AppConfig, MonitorConfig, TVMapping
from tvwall.services.config_repository import ConfigRepository


def test_config_normalization_clamps_values() -> None:
    config = AppConfig(
        input_width=0,
        input_height=0,
        framerate=0,
        number_tvs=0,
        selected_input_index=99,
        canvas_width=0,
        canvas_height=0,
        number_monitors=0,
        monitor_selected=5,
        monitor_data=[MonitorConfig(tv_layout="weird", tv_number=99, tv_first=99)],
        tv_mappings=[],
    )
    config.ensure_lengths()

    assert config.input_width >= 64
    assert config.input_height >= 64
    assert config.framerate >= 1
    assert config.number_tvs == 1
    assert len(config.tv_mappings) == 1
    assert config.monitor_selected == 0
    assert config.monitor_data[0].tv_layout == "1"
    assert config.monitor_data[0].tv_first == 1


def test_repository_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    repo = ConfigRepository()
    config = AppConfig(
        number_tvs=2,
        monitor_data=[MonitorConfig(tv_layout="2x2", tv_number=2, tv_first=1)],
        tv_mappings=[
            TVMapping(width=100, height=200, x_pos=10, y_pos=20),
            TVMapping(width=300, height=400, x_pos=30, y_pos=40),
        ],
    )

    repo.save(path, config)
    loaded = repo.load(path)

    assert loaded.number_tvs == 2
    assert loaded.monitor_data[0].tv_layout == "2x2"
    assert loaded.tv_mappings[1].width == 300
