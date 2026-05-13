from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from tvwall.domain import SOURCE_LABELS
from tvwall.domain.models import AppState
from tvwall.services.layout_service import LayoutService


class SourceService:
    def __init__(self, assets_dir: Path) -> None:
        self.assets_dir = assets_dir
        self.testcards = [
            Image.open(self.assets_dir / "testcard_01.png").convert("RGB"),
            Image.open(self.assets_dir / "testcard_grid.jpg").convert("RGB"),
        ]
        self._resized_testcard_cache: dict[tuple[int, int, int], Image.Image] = {}
        self._maptest_cache_key: tuple[int, int, int] | None = None
        self._maptest_cache_image: Image.Image | None = None

    def labels(self) -> tuple[str, ...]:
        return SOURCE_LABELS

    def build_source_image(self, state: AppState) -> Image.Image:
        if state.current_source_index == 2:
            return self._build_maptest_image(state)
        base = self.testcards[state.current_source_index]
        cache_key = (state.current_source_index, state.config.input_width, state.config.input_height)
        cached = self._resized_testcard_cache.get(cache_key)
        if cached is None:
            cached = base.resize((state.config.input_width, state.config.input_height))
            self._resized_testcard_cache[cache_key] = cached
        return cached

    def _build_maptest_image(self, state: AppState) -> Image.Image:
        cache_key = (state.source_revision, state.config.input_width, state.config.input_height)
        if self._maptest_cache_key == cache_key and self._maptest_cache_image is not None:
            return self._maptest_cache_image
        image = Image.new("RGB", (state.config.input_width, state.config.input_height), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        for tv_index in LayoutService.visible_tv_indices(state):
            tv = state.config.tv_mappings[tv_index - 1]
            color = (255, 0, 25) if tv_index == state.selected_tv else (0, 0, 255)
            x0 = int(tv.x_pos / state.config.canvas_width * state.config.input_width)
            y0 = int(tv.y_pos / state.config.canvas_height * state.config.input_height)
            x1 = int((tv.x_pos + tv.width) / state.config.canvas_width * state.config.input_width)
            y1 = int((tv.y_pos + tv.height) / state.config.canvas_height * state.config.input_height)
            draw.rectangle([x0, y0, x1, y1], outline=color, width=4)
            draw.text((x0 + 8, y0 + 8), str(tv_index), fill=(0, 255, 255))
        self._maptest_cache_key = cache_key
        self._maptest_cache_image = image
        return image
