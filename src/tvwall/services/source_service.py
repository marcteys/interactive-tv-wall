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

    def labels(self) -> tuple[str, ...]:
        return SOURCE_LABELS

    def build_source_image(self, state: AppState) -> Image.Image:
        if state.current_source_index == 2:
            return self._build_maptest_image(state)
        base = self.testcards[state.current_source_index]
        return base.resize((state.config.input_width, state.config.input_height))

    def _build_maptest_image(self, state: AppState) -> Image.Image:
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
        return image
