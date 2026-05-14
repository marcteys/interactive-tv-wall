from __future__ import annotations

from pathlib import Path

from tvwall.app.controller import AppController
from tvwall.ui.widgets import PanelAction


def test_controller_bootstrap_and_save_load(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    controller = AppController(config_path)

    controller.handle_action(PanelAction("adjust_tv_count", {"delta": 2}))
    controller.handle_action(PanelAction("adjust_canvas", {"field": "canvas_width", "delta": 100}))
    controller.handle_action(PanelAction("set_layout", {"index": 1}))
    controller.save()

    reloaded = AppController(config_path)
    assert reloaded.state.config.number_tvs == 3
    assert reloaded.state.config.canvas_width == 5100
    assert reloaded.state.active_monitor.tv_layout == "2x2"


def test_keyboard_moves_and_grid_cycle(tmp_path: Path) -> None:
    controller = AppController(tmp_path / "config.json")
    start_x = controller.state.config.tv_mappings[0].x_pos
    controller.keyboard_move(x_direction=1, resize=False)
    assert controller.state.config.tv_mappings[0].x_pos == start_x + controller.state.grid_size
    controller.cycle_grid(1)
    assert controller.state.grid_size == 50


def test_controller_supports_absolute_numeric_updates(tmp_path: Path) -> None:
    controller = AppController(tmp_path / "config.json")
    controller.handle_action(PanelAction("set_canvas_value", {"field": "canvas_width", "value": 6400}))
    controller.handle_action(PanelAction("set_monitor_count", {"value": 2}))
    controller.handle_action(PanelAction("set_monitor_field", {"field": "tv_first", "value": 1}))
    controller.handle_action(PanelAction("set_tv_count", {"value": 3}))
    controller.handle_action(PanelAction("set_selected_tv_value", {"value": 2}))
    controller.handle_action(PanelAction("set_tv_value", {"index": 2, "field": "x_pos", "value": 345}))

    assert controller.state.config.canvas_width == 6400
    assert controller.state.config.number_monitors == 2
    assert controller.state.selected_tv == 2
    assert controller.state.config.tv_mappings[1].x_pos == 345
