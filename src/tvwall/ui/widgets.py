from __future__ import annotations

from dataclasses import dataclass, field

import pyglet
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

    def reset(self) -> None:
        self.regions = []
        self._shape_count = 0
        self._label_count = 0

    def hit_test(self, x: float, y: float) -> PanelAction | None:
        for region in reversed(self.regions):
            if region.rect.contains(x, y):
                return region.action
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
        self.batch.draw()

    def panel(self, rect: Rect) -> None:
        shape = self._acquire_shape()
        shape.x = rect.x
        shape.y = rect.y
        shape.width = rect.width
        shape.height = rect.height
        shape.color = (24, 24, 30)
        shape.border_color = (52, 52, 62)

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

    def button(self, rect: Rect, label: str, action: PanelAction, active: bool = False) -> None:
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
        self.regions.append(InteractiveRegion(rect, action))

    def toggle(self, rect: Rect, label: str, value: bool, action: PanelAction) -> None:
        state = "ON" if value else "OFF"
        self.button(rect, f"{label}: {state}", action, active=value)

    def segmented(self, x: float, y: float, width: float, height: float, labels: list[str], selected: int, command: str) -> None:
        gap = 6
        segment_width = max(60, (width - gap * (len(labels) - 1)) / max(len(labels), 1))
        for index, label in enumerate(labels):
            rect = Rect(x + index * (segment_width + gap), y, segment_width, height)
            self.button(rect, label, PanelAction(command, {"index": index}), active=index == selected)

    def stepper(self, x: float, y: float, width: float, label: str, value: str, minus_action: PanelAction, plus_action: PanelAction) -> None:
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
        self.button(minus_rect, "-", minus_action)
        shape = self._acquire_shape()
        shape.x = value_rect.x
        shape.y = value_rect.y
        shape.width = value_rect.width
        shape.height = value_rect.height
        shape.color = (30, 30, 36)
        shape.border_color = (80, 80, 90)
        value_label = self._acquire_label()
        value_label.text = value
        value_label.x = value_rect.x + value_rect.width / 2
        value_label.y = value_rect.y + value_rect.height / 2
        value_label.width = 0
        value_label.multiline = False
        value_label.anchor_x = "center"
        value_label.anchor_y = "center"
        value_label.color = (245, 245, 245, 255)
        self.button(plus_rect, "+", plus_action)
