from __future__ import annotations

import pyglet
from pyglet import shapes

from tvwall.domain.models import AppState, Rect
from tvwall.services.layout_service import LayoutService


class MapPreviewRenderer:
    def __init__(self) -> None:
        self.batch = pyglet.graphics.Batch()
        self._shape_pool: list[shapes.BorderedRectangle] = []
        self._label_pool: list[pyglet.text.Label] = []
        self._shape_count = 0
        self._label_count = 0

    def _reset(self) -> None:
        self._shape_count = 0
        self._label_count = 0

    def _shape(self) -> shapes.BorderedRectangle:
        if self._shape_count >= len(self._shape_pool):
            self._shape_pool.append(
                shapes.BorderedRectangle(0, 0, 1, 1, border=1, color=(0, 0, 0), border_color=(0, 0, 0), batch=self.batch)
            )
        shape = self._shape_pool[self._shape_count]
        self._shape_count += 1
        shape.visible = True
        return shape

    def _label(self) -> pyglet.text.Label:
        if self._label_count >= len(self._label_pool):
            self._label_pool.append(pyglet.text.Label("", x=0, y=0, batch=self.batch))
        label = self._label_pool[self._label_count]
        self._label_count += 1
        label.visible = True
        return label

    def _finish(self) -> None:
        for shape in self._shape_pool[self._shape_count :]:
            shape.visible = False
        for label in self._label_pool[self._label_count :]:
            label.visible = False
        self.batch.draw()

    def draw(self, state: AppState, rect: Rect) -> None:
        self._reset()
        panel = self._shape()
        panel.x = rect.x
        panel.y = rect.y
        panel.width = rect.width
        panel.height = rect.height
        panel.color = (15, 15, 18)
        panel.border_color = (52, 52, 62)

        for tv_index in LayoutService.visible_tv_indices(state):
            tv = state.config.tv_mappings[tv_index - 1]
            px = rect.x + tv.x_pos / state.config.canvas_width * rect.width
            py = rect.y + tv.y_pos / state.config.canvas_height * rect.height
            pw = max(2, abs(tv.width) / state.config.canvas_width * rect.width)
            ph = max(2, abs(tv.height) / state.config.canvas_height * rect.height)
            draw_x = px if tv.width >= 0 else px - pw
            draw_y = py if tv.height >= 0 else py - ph
            border = (255, 64, 92) if tv_index == state.selected_tv else (64, 134, 255)
            shape = self._shape()
            shape.x = draw_x
            shape.y = draw_y
            shape.width = pw
            shape.height = ph
            shape.color = (8, 8, 10)
            shape.border_color = border
            label = self._label()
            label.text = str(tv_index)
            label.x = draw_x + pw / 2
            label.y = draw_y + ph / 2
            label.width = 0
            label.multiline = False
            label.anchor_x = "center"
            label.anchor_y = "center"
            label.color = (0, 255, 255, 255)
        self._finish()
