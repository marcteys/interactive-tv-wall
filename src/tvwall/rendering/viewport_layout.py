from __future__ import annotations

from dataclasses import dataclass

from tvwall.domain.models import Rect


@dataclass(frozen=True)
class ViewportLayout:
    panel_rect: Rect
    output_rect: Rect
    map_rect: Rect
    footer_rect: Rect

    @classmethod
    def compute(cls, width: int, height: int) -> "ViewportLayout":
        padding = 16
        panel_width = max(360, min(460, int(width * 0.34)))
        content_width = max(320, width - panel_width - padding * 3)
        output_height = max(220, int((height - padding * 3) * 0.58))
        map_height = max(180, height - output_height - padding * 3)

        panel = Rect(padding, padding, panel_width, height - padding * 2)
        output = Rect(panel.right + padding, height - output_height - padding, content_width, output_height)
        map_rect = Rect(panel.right + padding, padding + 44, content_width, map_height - 44)
        footer = Rect(panel.right + padding, padding, content_width, 32)
        return cls(panel, output, map_rect, footer)
