from __future__ import annotations

from tvwall.domain.models import AppConfig, AppState, MonitorConfig, Rect, TVMapping
from tvwall.services.layout_service import LayoutService


def make_state() -> AppState:
    config = AppConfig(
        number_tvs=4,
        monitor_data=[MonitorConfig(tv_layout="2x2", tv_number=2, tv_first=2)],
        tv_mappings=[
            TVMapping(width=100, height=100, x_pos=0, y_pos=0),
            TVMapping(width=100, height=100, x_pos=120, y_pos=0),
            TVMapping(width=-100, height=100, x_pos=320, y_pos=0),
            TVMapping(width=100, height=-100, x_pos=0, y_pos=160),
        ],
        monitor_focus=True,
    )
    config.ensure_lengths()
    state = AppState(config=config, current_source_index=0, selected_tv=2)
    return state


def test_visible_indices_respect_monitor_focus() -> None:
    state = make_state()
    assert LayoutService.visible_tv_indices(state) == [2, 3]


def test_normalize_selection_falls_back_to_visible_range() -> None:
    state = make_state()
    state.selected_tv = 4
    LayoutService.normalize_selection(state)
    assert state.selected_tv == 2


def test_set_layout_updates_tv_number() -> None:
    state = make_state()
    LayoutService.set_layout(state, "3x3")
    assert state.active_monitor.tv_layout == "3x3"
    assert state.active_monitor.tv_number == 4


def test_hit_test_handles_negative_dimensions() -> None:
    state = make_state()
    rect = Rect(0, 0, 420, 420)
    state.config.monitor_focus = False
    hit = LayoutService.hit_test(state, rect, 22, 5)
    assert hit == 3


def test_drag_selected_moves_and_resizes() -> None:
    state = make_state()
    rect = Rect(0, 0, 500, 500)
    assert LayoutService.begin_drag(state, rect, 15, 5) is True
    LayoutService.drag_selected(state, rect, 28, 12, resize=False)
    assert state.config.tv_mappings[1].x_pos > 120
    LayoutService.drag_selected(state, rect, 40, 20, resize=True)
    assert state.config.tv_mappings[1].width != 100


def test_pack_tv_uniforms_is_stable() -> None:
    state = make_state()
    packed, count = LayoutService.pack_tv_uniforms(state.config.tv_mappings, 0, 3)
    assert count == 3
    assert len(packed) == 9 * 4 * 4
