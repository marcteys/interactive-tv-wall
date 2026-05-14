from __future__ import annotations

from dataclasses import dataclass, field

import pyglet
from pyglet import gl
from pyglet import shapes

from tvwall.domain.models import Rect


@dataclass
class PanelAction:
    command: str
    payload: dict = field(default_factory=dict)


@dataclass
class InteractiveRegion:
    rect: Rect
    action: PanelAction
    tooltip: str | None = None


class WidgetPainter:
    """Stateless painter that accumulates interactive regions during drawing.

    Contract: hit_test() queries the regions built by the most recent draw pass.
    draw() (via the owning view) must be called before hit_test() each frame;
    reset() clears regions at the start of each draw, so stale regions are never hit.
    """

    def __init__(self) -> None:
        self.batch = pyglet.graphics.Batch()
        self.regions: list[InteractiveRegion] = []
        self._shape_pool: list[shapes.BorderedRectangle] = []
        self._label_pool: list[pyglet.text.Label] = []
        self._shape_count = 0
        self._label_count = 0
        self._clip_rect: Rect | None = None

    def reset(self) -> None:
        self.regions = []
        self._shape_count = 0
        self._label_count = 0
        self._clip_rect = None

    def set_clip_rect(self, rect: Rect | None) -> None:
        self._clip_rect = rect

    def hit_test(self, x: float, y: float) -> PanelAction | None:
        for region in reversed(self.regions):
            if region.rect.contains(x, y):
                return region.action
        return None

    def tooltip_at(self, x: float, y: float) -> str | None:
        for region in reversed(self.regions):
            if region.tooltip and region.rect.contains(x, y):
                return region.tooltip
        return None

    def _acquire_shape(self) -> shapes.BorderedRectangle:
        if self._shape_count >= len(self._shape_pool):
            self._shape_pool.append(
                shapes.BorderedRectangle(0, 0, 1, 1, border=1, color=(0, 0, 0), border_color=(0, 0, 0), batch=self.batch)
            )
        shape = self._shape_pool[self._shape_count]
        self._shape_count += 1
        shape.visible = True
        return shape

    def _acquire_label(self) -> pyglet.text.Label:
        if self._label_count >= len(self._label_pool):
            self._label_pool.append(pyglet.text.Label("", x=0, y=0, batch=self.batch))
        label = self._label_pool[self._label_count]
        self._label_count += 1
        label.visible = True
        return label

    def finish(self) -> None:
        for shape in self._shape_pool[self._shape_count :]:
            shape.visible = False
        for label in self._label_pool[self._label_count :]:
            label.visible = False
        if self._clip_rect is None:
            self.batch.draw()
            return
        gl.glEnable(gl.GL_SCISSOR_TEST)
        gl.glScissor(
            int(self._clip_rect.x),
            int(self._clip_rect.y),
            max(0, int(self._clip_rect.width)),
            max(0, int(self._clip_rect.height)),
        )
        try:
            self.batch.draw()
        finally:
            gl.glDisable(gl.GL_SCISSOR_TEST)

    @staticmethod
    def _intersects(a: Rect, b: Rect) -> bool:
        return a.x < b.right and a.right > b.x and a.y < b.top and a.top > b.y

    def _is_visible(self, rect: Rect) -> bool:
        return self._clip_rect is None or self._intersects(rect, self._clip_rect)

    def panel(self, rect: Rect) -> None:
        shape = self._acquire_shape()
        shape.x = rect.x
        shape.y = rect.y
        shape.width = rect.width
        shape.height = rect.height
        shape.color = (24, 24, 30)
        shape.border_color = (52, 52, 62)

    def surface(self, rect: Rect, fill: tuple[int, int, int], border: tuple[int, int, int]) -> None:
        if not self._is_visible(rect):
            return
        shape = self._acquire_shape()
        shape.x = rect.x
        shape.y = rect.y
        shape.width = rect.width
        shape.height = rect.height
        shape.color = fill
        shape.border_color = border

    def section_title(self, x: float, y: float, text: str) -> None:
        label = self._acquire_label()
        label.text = text
        label.x = x
        label.y = y
        label.width = 0
        label.multiline = False
        label.anchor_x = "left"
        label.anchor_y = "baseline"
        label.color = (255, 255, 255, 255)

    def section_header(self, rect: Rect, title: str, expanded: bool, action: PanelAction, subtitle: str | None = None) -> None:
        if not self._is_visible(rect):
            return
        fill = (36, 38, 48)
        border = (84, 92, 118)
        shape = self._acquire_shape()
        shape.x = rect.x
        shape.y = rect.y
        shape.width = rect.width
        shape.height = rect.height
        shape.color = fill
        shape.border_color = border

        indicator = self._acquire_label()
        indicator.text = "v" if expanded else ">"
        indicator.x = rect.x + 14
        indicator.y = rect.y + rect.height / 2
        indicator.width = 0
        indicator.multiline = False
        indicator.anchor_x = "center"
        indicator.anchor_y = "center"
        indicator.color = (220, 228, 255, 255)

        title_label = self._acquire_label()
        title_label.text = title
        title_label.x = rect.x + 28
        title_label.y = rect.y + rect.height - 12
        title_label.width = max(120, int(rect.width - 40))
        title_label.multiline = False
        title_label.anchor_x = "left"
        title_label.anchor_y = "baseline"
        title_label.color = (255, 255, 255, 255)

        if subtitle:
            subtitle_label = self._acquire_label()
            subtitle_label.text = subtitle
            subtitle_label.x = rect.x + 28
            subtitle_label.y = rect.y + 10
            subtitle_label.width = max(120, int(rect.width - 40))
            subtitle_label.multiline = False
            subtitle_label.anchor_x = "left"
            subtitle_label.anchor_y = "baseline"
            subtitle_label.color = (188, 192, 210, 255)

        self.regions.append(InteractiveRegion(rect, action, f"Show or hide the {title.lower()} section."))

    def body_text(self, x: float, y: float, text: str, width: int = 360) -> None:
        label = self._acquire_label()
        label.text = text
        label.x = x
        label.y = y
        label.width = width
        label.multiline = True
        label.anchor_x = "left"
        label.anchor_y = "baseline"
        label.color = (210, 210, 220, 255)

    def button(self, rect: Rect, label: str, action: PanelAction, active: bool = False, tooltip: str | None = None) -> None:
        if not self._is_visible(rect):
            return
        fill = (72, 92, 170) if active else (42, 42, 50)
        border = (106, 130, 240) if active else (82, 82, 94)
        shape = self._acquire_shape()
        shape.x = rect.x
        shape.y = rect.y
        shape.width = rect.width
        shape.height = rect.height
        shape.color = fill
        shape.border_color = border

        text_label = self._acquire_label()
        text_label.text = label
        text_label.x = rect.x + rect.width / 2
        text_label.y = rect.y + rect.height / 2
        text_label.width = 0
        text_label.multiline = False
        text_label.anchor_x = "center"
        text_label.anchor_y = "center"
        text_label.color = (255, 255, 255, 255)
        self.regions.append(InteractiveRegion(rect, action, tooltip))

    def toggle(self, rect: Rect, label: str, value: bool, action: PanelAction, tooltip: str | None = None) -> None:
        state = "ON" if value else "OFF"
        self.button(rect, f"{label}: {state}", action, active=value, tooltip=tooltip)

    def segmented(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        labels: list[str],
        selected: int,
        command: str,
        tooltips: list[str] | None = None,
    ) -> None:
        gap = 6
        segment_width = max(60, (width - gap * (len(labels) - 1)) / max(len(labels), 1))
        for index, label in enumerate(labels):
            rect = Rect(x + index * (segment_width + gap), y, segment_width, height)
            tooltip = tooltips[index] if tooltips and index < len(tooltips) else None
            self.button(rect, label, PanelAction(command, {"index": index}), active=index == selected, tooltip=tooltip)

    def stepper(
        self,
        x: float,
        y: float,
        width: float,
        label: str,
        value: str,
        minus_action: PanelAction,
        plus_action: PanelAction,
        value_action: PanelAction | None = None,
        value_active: bool = False,
        tooltip: str | None = None,
    ) -> None:
        label_rect = Rect(x, y + 26, max(width, 1), 18)
        if self._is_visible(label_rect):
            text_label = self._acquire_label()
            text_label.text = label
            text_label.x = x
            text_label.y = y + 26
            text_label.width = 0
            text_label.multiline = False
            text_label.anchor_x = "left"
            text_label.anchor_y = "baseline"
            text_label.color = (220, 220, 220, 255)
        minus_rect = Rect(x, y, 28, 22)
        value_rect = Rect(x + 32, y, width - 64, 22)
        plus_rect = Rect(x + width - 28, y, 28, 22)
        self.button(minus_rect, "-", minus_action, tooltip=tooltip)
        if self._is_visible(value_rect):
            shape = self._acquire_shape()
            shape.x = value_rect.x
            shape.y = value_rect.y
            shape.width = value_rect.width
            shape.height = value_rect.height
            shape.color = (44, 50, 74) if value_active else (30, 30, 36)
            shape.border_color = (114, 140, 244) if value_active else (80, 80, 90)
            value_label = self._acquire_label()
            value_label.text = value
            value_label.x = value_rect.x + value_rect.width / 2
            value_label.y = value_rect.y + value_rect.height / 2
            value_label.width = 0
            value_label.multiline = False
            value_label.anchor_x = "center"
            value_label.anchor_y = "center"
            value_label.color = (245, 245, 245, 255)
            if value_action is not None:
                self.regions.append(InteractiveRegion(value_rect, value_action, tooltip))
        self.button(plus_rect, "+", plus_action, tooltip=tooltip)
