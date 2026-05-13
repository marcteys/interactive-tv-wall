from __future__ import annotations

import pyglet

from tvwall.domain.models import AppState, Rect
from tvwall.services.layout_service import LayoutService


class MapPreviewRenderer:
    def draw(self, state: AppState, rect: Rect) -> None:
        pyglet.shapes.BorderedRectangle(
            rect.x, rect.y, rect.width, rect.height, border=2, color=(15, 15, 18), border_color=(52, 52, 62)
        ).draw()

        for tv_index in LayoutService.visible_tv_indices(state):
            tv = state.config.tv_mappings[tv_index - 1]
            px = rect.x + tv.x_pos / state.config.canvas_width * rect.width
            py = rect.y + tv.y_pos / state.config.canvas_height * rect.height
            pw = max(2, abs(tv.width) / state.config.canvas_width * rect.width)
            ph = max(2, abs(tv.height) / state.config.canvas_height * rect.height)
            draw_x = px if tv.width >= 0 else px - pw
            draw_y = py if tv.height >= 0 else py - ph
            border = (255, 64, 92) if tv_index == state.selected_tv else (64, 134, 255)
            pyglet.shapes.BorderedRectangle(
                draw_x, draw_y, pw, ph, border=2, color=(8, 8, 10), border_color=border
            ).draw()
            pyglet.text.Label(
                str(tv_index),
                x=draw_x + pw / 2,
                y=draw_y + ph / 2,
                anchor_x="center",
                anchor_y="center",
                color=(0, 255, 255, 255),
            ).draw()
