from __future__ import annotations

from dataclasses import dataclass, field

import pyglet

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
    def __init__(self) -> None:
        self.regions: list[InteractiveRegion] = []

    def reset(self) -> None:
        self.regions = []

    def hit_test(self, x: float, y: float) -> PanelAction | None:
        for region in reversed(self.regions):
            if region.rect.contains(x, y):
                return region.action
        return None

    def panel(self, rect: Rect) -> None:
        pyglet.shapes.BorderedRectangle(
            rect.x, rect.y, rect.width, rect.height, border=1, color=(24, 24, 30), border_color=(52, 52, 62)
        ).draw()

    def section_title(self, x: float, y: float, text: str) -> None:
        pyglet.text.Label(text, x=x, y=y, bold=True, color=(255, 255, 255, 255)).draw()

    def body_text(self, x: float, y: float, text: str, width: int = 360) -> None:
        pyglet.text.Label(text, x=x, y=y, multiline=True, width=width, color=(210, 210, 220, 255)).draw()

    def button(self, rect: Rect, label: str, action: PanelAction, active: bool = False) -> None:
        fill = (72, 92, 170) if active else (42, 42, 50)
        border = (106, 130, 240) if active else (82, 82, 94)
        pyglet.shapes.BorderedRectangle(rect.x, rect.y, rect.width, rect.height, border=1, color=fill, border_color=border).draw()
        pyglet.text.Label(
            label,
            x=rect.x + rect.width / 2,
            y=rect.y + rect.height / 2,
            anchor_x="center",
            anchor_y="center",
            color=(255, 255, 255, 255),
        ).draw()
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
        pyglet.text.Label(label, x=x, y=y + 26, color=(220, 220, 220, 255)).draw()
        minus_rect = Rect(x, y, 28, 22)
        value_rect = Rect(x + 32, y, width - 64, 22)
        plus_rect = Rect(x + width - 28, y, 28, 22)
        self.button(minus_rect, "-", minus_action)
        pyglet.shapes.BorderedRectangle(
            value_rect.x, value_rect.y, value_rect.width, value_rect.height, border=1, color=(30, 30, 36), border_color=(80, 80, 90)
        ).draw()
        pyglet.text.Label(
            value,
            x=value_rect.x + value_rect.width / 2,
            y=value_rect.y + value_rect.height / 2,
            anchor_x="center",
            anchor_y="center",
            color=(245, 245, 245, 255),
        ).draw()
        self.button(plus_rect, "+", plus_action)
