from __future__ import annotations

from pathlib import Path

from tvwall.domain.models import AppConfig, AppState
from tvwall.services.source_service import SourceService


def test_source_service_builds_testmap_image() -> None:
    assets_dir = Path(__file__).resolve().parents[1] / "assets" / "source_data"
    service = SourceService(assets_dir)
    config = AppConfig(number_tvs=1)
    config.ensure_lengths()
    state = AppState(config=config, current_source_index=2, selected_tv=1)

    image = service.build_source_image(state)

    assert image.size == (config.input_width, config.input_height)


def test_source_service_caches_testcard_resizes() -> None:
    assets_dir = Path(__file__).resolve().parents[1] / "assets" / "source_data"
    service = SourceService(assets_dir)
    config = AppConfig(number_tvs=1)
    config.ensure_lengths()
    state = AppState(config=config, current_source_index=0, selected_tv=1)

    image_a = service.build_source_image(state)
    image_b = service.build_source_image(state)

    assert image_a is image_b


def test_source_service_caches_maptest_between_unchanged_revisions() -> None:
    assets_dir = Path(__file__).resolve().parents[1] / "assets" / "source_data"
    service = SourceService(assets_dir)
    config = AppConfig(number_tvs=1)
    config.ensure_lengths()
    state = AppState(config=config, current_source_index=2, selected_tv=1)

    image_a = service.build_source_image(state)
    image_b = service.build_source_image(state)

    assert image_a is image_b
