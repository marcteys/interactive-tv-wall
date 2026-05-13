from __future__ import annotations

import json
from array import array
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List

import moderngl
import pyglet
from PIL import Image, ImageDraw
from pyglet import gl
from pyglet.window import key, mouse


MAX_TVS_PER_LAYOUT = 9
GRID_OPTIONS = [100, 50, 10, 5, 1]
LAYOUT_TO_COUNT = {"1": 1, "2x2": 4, "3x3": 9}
SOURCE_TYPES = ("TESTCARD_0", "TESTCARD_1", "TESTMAP")

VERTEX_SHADER = """
#version 330
in vec2 in_pos;
in vec2 in_uv;
out vec2 v_uv;
void main() {
    v_uv = in_uv;
    gl_Position = vec4(in_pos, 0.0, 1.0);
}
"""

FRAGMENT_SHADER = """
#version 330
uniform sampler2D u_tex0;
uniform ivec2 u_canvas;
uniform int u_layout_mode;
uniform int u_tv_count;
uniform ivec4 u_tvdata[9];
in vec2 v_uv;
out vec4 fragColor;

vec4 sample_tv(vec2 pos, ivec4 tvdata, float x_slots, float y_slots, float x_index, float y_index) {
    float tv_width = float(tvdata.x) / float(max(u_canvas.x, 1));
    float tv_height = float(tvdata.y) / float(max(u_canvas.y, 1));
    float tv_x = float(tvdata.z) / float(max(u_canvas.x, 1));
    float tv_y = float(tvdata.w) / float(max(u_canvas.y, 1));
    vec2 mapped = pos;

    if (abs(tv_width) < abs(tv_height)) {
        float temp = mapped.x;
        mapped.x = tv_x + tv_width - x_slots * tv_width * (mapped.y - y_index / y_slots);
        mapped.y = tv_y + y_slots * tv_height * (temp - x_index / x_slots);
    } else {
        mapped.x = tv_x + x_slots * tv_width * (mapped.x - x_index / x_slots);
        mapped.y = tv_y + y_slots * tv_height * (mapped.y - y_index / y_slots);
    }

    return texture(u_tex0, mapped);
}

void main() {
    if (u_layout_mode == 0) {
        fragColor = sample_tv(v_uv, u_tvdata[0], 1.0, 1.0, 0.0, 0.0);
        return;
    }

    if (u_layout_mode == 1) {
        int x_index = int(floor(v_uv.x * 2.0));
        int y_index = int(floor(v_uv.y * 2.0));
        int tv_index = clamp(y_index * 2 + x_index, 0, min(u_tv_count, 4) - 1);
        fragColor = sample_tv(v_uv, u_tvdata[tv_index], 2.0, 2.0, float(x_index), float(y_index));
        return;
    }

    int x_index = min(int(floor(v_uv.x * 3.0)), 2);
    int y_index = min(int(floor(v_uv.y * 3.0)), 2);
    int tv_index = clamp(y_index * 3 + x_index, 0, min(u_tv_count, 9) - 1);
    fragColor = sample_tv(v_uv, u_tvdata[tv_index], 3.0, 3.0, float(x_index), float(y_index));
}
"""


@dataclass
class TVData:
    width: int = 1000
    height: int = 1000
    x_pos: int = 0
    y_pos: int = 0


@dataclass
class MonitorData:
    output_to_monitor: bool = True
    output_to_ndi: bool = False
    is_fullscreen: bool = False
    display_index: int = 0
    tv_number: int = 1
    tv_first: int = 1
    tv_layout: str = "1"


@dataclass
class AppConfig:
    hide_maptest: bool = False
    hide_preview: bool = False
    set_resolutions: bool = False
    input_width: int = 1920
    input_height: int = 1080
    framerate: int = 30
    number_tvs: int = 1
    selected_input_index: int = 0
    canvas_width: int = 5000
    canvas_height: int = 5000
    number_monitors: int = 1
    monitor_selected: int = 0
    monitor_focus: bool = False
    monitor_data: List[MonitorData] = field(default_factory=lambda: [MonitorData()])
    tv_mappings: List[TVData] = field(default_factory=lambda: [TVData()])

    @classmethod
    def from_json(cls, path: Path) -> "AppConfig":
        if not path.exists():
            return cls()
        data = json.loads(path.read_text(encoding="utf-8"))
        config = cls(
            hide_maptest=data.get("hide_maptest", False),
            hide_preview=data.get("hide_preview", False),
            set_resolutions=data.get("set_resolutions", False),
            input_width=data.get("input_width", 1920),
            input_height=data.get("input_height", 1080),
            framerate=data.get("framerate", 30),
            number_tvs=max(1, data.get("number_tvs", 1)),
            selected_input_index=data.get("selected_input_index", 0),
            canvas_width=max(1, data.get("canvas_width", 5000)),
            canvas_height=max(1, data.get("canvas_height", 5000)),
            number_monitors=max(1, data.get("number_monitors", 1)),
            monitor_selected=data.get("monitor_selected", 0),
            monitor_focus=data.get("monitor_focus", False),
            monitor_data=[MonitorData(**item) for item in data.get("monitor_data", [])] or [MonitorData()],
            tv_mappings=[TVData(**item) for item in data.get("tv_mappings", [])] or [TVData()],
        )
        config.ensure_lengths()
        return config

    def ensure_lengths(self) -> None:
        self.number_tvs = max(1, self.number_tvs)
        while len(self.tv_mappings) < self.number_tvs:
            self.tv_mappings.append(TVData())
        if len(self.tv_mappings) > self.number_tvs:
            self.tv_mappings = self.tv_mappings[: self.number_tvs]
        if not self.monitor_data:
            self.monitor_data = [MonitorData()]
        self.number_monitors = max(1, len(self.monitor_data))
        self.monitor_selected = max(0, min(self.monitor_selected, self.number_monitors - 1))
        self.selected_input_index = max(0, min(self.selected_input_index, len(SOURCE_TYPES) - 1))
        for monitor in self.monitor_data:
            monitor.tv_layout = monitor.tv_layout if monitor.tv_layout in LAYOUT_TO_COUNT else "1"
            monitor.tv_number = max(1, min(monitor.tv_number, MAX_TVS_PER_LAYOUT))
            monitor.tv_first = max(1, min(monitor.tv_first, self.number_tvs))

    def to_json(self) -> dict:
        return {
            "hide_maptest": self.hide_maptest,
            "hide_preview": self.hide_preview,
            "set_resolutions": self.set_resolutions,
            "input_width": self.input_width,
            "input_height": self.input_height,
            "framerate": self.framerate,
            "number_tvs": self.number_tvs,
            "selected_input_index": self.selected_input_index,
            "canvas_width": self.canvas_width,
            "canvas_height": self.canvas_height,
            "number_monitors": self.number_monitors,
            "monitor_selected": self.monitor_selected,
            "monitor_focus": self.monitor_focus,
            "monitor_data": [asdict(item) for item in self.monitor_data],
            "tv_mappings": [asdict(item) for item in self.tv_mappings],
        }


class MapperWindow(pyglet.window.Window):
    def __init__(self) -> None:
        self.project_root = Path(__file__).resolve().parents[1]
        self.assets_dir = self.project_root / "assets" / "source_data"
        self.config_path = self.project_root / "config.json"
        self.config = AppConfig.from_json(self.config_path)
        self.config.ensure_lengths()
        display_config = gl.Config(double_buffer=True, major_version=3, minor_version=3, depth_size=24)
        super().__init__(1280, 720, "TV Wall Mapper Python Port", resizable=True, config=display_config)
        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.BLEND)
        self.program = self.ctx.program(vertex_shader=VERTEX_SHADER, fragment_shader=FRAGMENT_SHADER)
        quad = self.ctx.buffer(
            data=array("f", (
                -1.0, -1.0, 0.0, 0.0,
                1.0, -1.0, 1.0, 0.0,
                -1.0, 1.0, 0.0, 1.0,
                1.0, 1.0, 1.0, 1.0,
            )).tobytes()
        )
        self.quad = self.ctx.simple_vertex_array(self.program, quad, "in_pos", "in_uv")
        self.current_source = self.config.selected_input_index
        self.selected_tv = 1
        self.grid_index = 0
        self.drag_button: int | None = None
        self.drag_offset = (0.0, 0.0)
        self.shift_pressed = False
        self.alt_pressed = False
        self.status_message = "Loaded default config"
        self.preview_label = pyglet.text.Label("", x=16, y=self.height - 16, anchor_x="left", anchor_y="top", color=(255, 255, 255, 255))
        self.help_label = pyglet.text.Label(
            "",
            x=16,
            y=16,
            width=460,
            multiline=True,
            anchor_x="left",
            anchor_y="bottom",
            color=(220, 220, 220, 255),
        )
        self.output_label = pyglet.text.Label("", x=self.width - 16, y=self.height - 16, anchor_x="right", anchor_y="top", color=(255, 255, 255, 255))
        self._load_textures()
        pyglet.clock.schedule_interval(self._tick, 1.0 / max(self.config.framerate, 1))

    def _load_textures(self) -> None:
        self.testcard_images = [
            Image.open(self.assets_dir / "testcard_01.png").convert("RGB"),
            Image.open(self.assets_dir / "testcard_grid.jpg").convert("RGB"),
        ]
        self.source_texture = self.ctx.texture(
            self.testcard_images[0].size,
            3,
            self.testcard_images[0].transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes(),
        )
        self.source_texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self.source_texture.repeat_x = False
        self.source_texture.repeat_y = False
        self._refresh_source_texture()

    @property
    def active_monitor(self) -> MonitorData:
        index = min(self.config.monitor_selected, len(self.config.monitor_data) - 1)
        return self.config.monitor_data[index]

    @property
    def grid_size(self) -> int:
        return GRID_OPTIONS[self.grid_index]

    def _refresh_source_texture(self) -> None:
        image = self._build_source_image()
        if self.source_texture.size != image.size:
            self.source_texture.release()
            self.source_texture = self.ctx.texture(image.size, 3, image.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes())
            self.source_texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
        else:
            self.source_texture.write(image.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes())

    def _build_source_image(self) -> Image.Image:
        if self.current_source == 2:
            return self._build_maptest_image()
        return self.testcard_images[self.current_source].resize((self.config.input_width, self.config.input_height))

    def _build_maptest_image(self) -> Image.Image:
        image = Image.new("RGB", (self.config.input_width, self.config.input_height), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        for index in self._visible_tv_indices():
            tv = self.config.tv_mappings[index - 1]
            color = (255, 0, 25) if index == self.selected_tv else (0, 0, 255)
            x0 = int(tv.x_pos / self.config.canvas_width * self.config.input_width)
            y0 = int(tv.y_pos / self.config.canvas_height * self.config.input_height)
            x1 = int((tv.x_pos + tv.width) / self.config.canvas_width * self.config.input_width)
            y1 = int((tv.y_pos + tv.height) / self.config.canvas_height * self.config.input_height)
            draw.rectangle([x0, y0, x1, y1], outline=color, width=4)
            draw.text((x0 + 8, y0 + 8), str(index), fill=(0, 255, 255))
        return image

    def _visible_tv_indices(self) -> List[int]:
        if not self.config.monitor_focus:
            return list(range(1, self.config.number_tvs + 1))
        start = self.active_monitor.tv_first
        end = min(start + self.active_monitor.tv_number - 1, self.config.number_tvs)
        return list(range(start, end + 1))

    def _visible_tvs(self) -> List[TVData]:
        return [self.config.tv_mappings[index - 1] for index in self._visible_tv_indices()]

    def _tick(self, dt: float) -> None:
        self._refresh_source_texture()

    def on_draw(self) -> None:
        self.clear()
        self.ctx.clear(0.08, 0.08, 0.1, 1.0)
        map_rect = self._map_rect()
        output_rect = self._output_rect()
        if not self.config.hide_preview:
            self._draw_shader_output(output_rect)
        if not self.config.hide_maptest:
            self._draw_map_preview(map_rect)
        self._draw_labels(map_rect, output_rect)

    def _draw_shader_output(self, rect: tuple[int, int, int, int]) -> None:
        x, y, width, height = rect
        self.ctx.viewport = (x, y, width, height)
        self.source_texture.use(0)
        self.program["u_tex0"] = 0
        self.program["u_canvas"] = (self.config.canvas_width, self.config.canvas_height)
        layout = self.active_monitor.tv_layout
        self.program["u_layout_mode"] = {"1": 0, "2x2": 1, "3x3": 2}[layout]
        tv_indices = []
        start_index = max(0, self.active_monitor.tv_first - 1)
        for offset in range(MAX_TVS_PER_LAYOUT):
            tv_index = min(start_index + offset, len(self.config.tv_mappings) - 1)
            tv_indices.append(self.config.tv_mappings[tv_index])
        self.program["u_tv_count"] = min(self.active_monitor.tv_number, MAX_TVS_PER_LAYOUT)
        self.program["u_tvdata"].write(
            b"".join(
                int(value).to_bytes(4, "little", signed=True)
                for tv in tv_indices
                for value in (tv.width, tv.height, tv.x_pos, tv.y_pos)
            )
        )
        self.quad.render(moderngl.TRIANGLE_STRIP)
        self.ctx.viewport = (0, 0, self.width, self.height)

    def _draw_map_preview(self, rect: tuple[int, int, int, int]) -> None:
        x, y, width, height = rect
        pyglet.shapes.Rectangle(x, y, width, height, color=(18, 18, 18)).draw()
        for tv_index in self._visible_tv_indices():
            tv = self.config.tv_mappings[tv_index - 1]
            px = x + tv.x_pos / self.config.canvas_width * width
            py = y + tv.y_pos / self.config.canvas_height * height
            pw = max(2, abs(tv.width) / self.config.canvas_width * width)
            ph = max(2, abs(tv.height) / self.config.canvas_height * height)
            draw_x = px if tv.width >= 0 else px - pw
            draw_y = py if tv.height >= 0 else py - ph
            border = (255, 0, 25) if tv_index == self.selected_tv else (0, 0, 255)
            pyglet.shapes.BorderedRectangle(draw_x, draw_y, pw, ph, border=2, color=(10, 10, 10), border_color=border).draw()
            pyglet.text.Label(
                str(tv_index),
                x=draw_x + pw / 2,
                y=draw_y + ph / 2,
                anchor_x="center",
                anchor_y="center",
                color=(0, 255, 255, 255),
            ).draw()

    def _draw_labels(self, map_rect: tuple[int, int, int, int], output_rect: tuple[int, int, int, int]) -> None:
        self.preview_label.text = (
            f"Source: {SOURCE_TYPES[self.current_source]} | Layout: {self.active_monitor.tv_layout} | "
            f"Selected TV: {self.selected_tv} | Grid: {self.grid_size}mm"
        )
        self.preview_label.y = self.height - 16
        self.preview_label.draw()
        self.output_label.text = (
            f"Canvas {self.config.canvas_width}x{self.config.canvas_height} mm | "
            f"Input {self.config.input_width}x{self.config.input_height} px"
        )
        self.output_label.x = self.width - 16
        self.output_label.y = self.height - 16
        self.output_label.draw()
        self.help_label.text = (
            "Mouse: left select/move, shift-drag or right-drag resize\n"
            "Keys: arrows move, shift+arrows resize, alt+left/right choose TV, alt+up/down grid\n"
            "1/2/3 switch layout, I cycle source, M map source, S save, L load, F fullscreen\n"
            f"Status: {self.status_message}"
        )
        self.help_label.draw()
        pyglet.text.Label("MAP PREVIEW", x=map_rect[0], y=map_rect[1] + map_rect[3] + 10, color=(255, 255, 255, 255)).draw()
        pyglet.text.Label("OUTPUT PREVIEW", x=output_rect[0], y=output_rect[1] + output_rect[3] + 10, color=(255, 255, 255, 255)).draw()

    def _map_rect(self) -> tuple[int, int, int, int]:
        padding = 24
        width = max(260, int(self.width * 0.38))
        height = self.height - padding * 3 - 24
        return padding, padding + 24, width, height

    def _output_rect(self) -> tuple[int, int, int, int]:
        padding = 24
        map_x, _, map_width, _ = self._map_rect()
        x = map_x + map_width + padding
        width = max(320, self.width - x - padding)
        height = self.height - padding * 3 - 24
        return x, padding + 24, width, height

    def _map_coordinates_to_canvas(self, x: float, y: float) -> tuple[float, float] | None:
        rect_x, rect_y, rect_w, rect_h = self._map_rect()
        if not (rect_x <= x <= rect_x + rect_w and rect_y <= y <= rect_y + rect_h):
            return None
        local_x = (x - rect_x) / rect_w * self.config.canvas_width
        local_y = (y - rect_y) / rect_h * self.config.canvas_height
        return local_x, local_y

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        canvas_point = self._map_coordinates_to_canvas(x, y)
        if canvas_point is None:
            return
        self.drag_button = button
        canvas_x, canvas_y = canvas_point
        focused = 0
        for tv_index in reversed(self._visible_tv_indices()):
            tv = self.config.tv_mappings[tv_index - 1]
            x_min, x_max = sorted((tv.x_pos, tv.x_pos + tv.width))
            y_min, y_max = sorted((tv.y_pos, tv.y_pos + tv.height))
            if x_min <= canvas_x <= x_max and y_min <= canvas_y <= y_max:
                focused = tv_index
                break
        if focused:
            self.selected_tv = focused
            tv = self.config.tv_mappings[self.selected_tv - 1]
            self.drag_offset = (canvas_x - tv.x_pos, canvas_y - tv.y_pos)
            self.status_message = f"Selected TV {self.selected_tv}"
        else:
            self.status_message = "Clicked outside any TV region"

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int) -> None:
        if self.selected_tv <= 0:
            return
        canvas_point = self._map_coordinates_to_canvas(x, y)
        if canvas_point is None:
            return
        tv = self.config.tv_mappings[self.selected_tv - 1]
        canvas_x, canvas_y = canvas_point
        if buttons & mouse.RIGHT or modifiers & key.MOD_SHIFT:
            tv.width = int(canvas_x - tv.x_pos)
            tv.height = int(canvas_y - tv.y_pos)
            self.status_message = f"Resized TV {self.selected_tv}"
        else:
            tv.x_pos = int(canvas_x - self.drag_offset[0])
            tv.y_pos = int(canvas_y - self.drag_offset[1])
            self.status_message = f"Moved TV {self.selected_tv}"

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        self.shift_pressed = bool(modifiers & key.MOD_SHIFT)
        self.alt_pressed = bool(modifiers & key.MOD_ALT)
        if symbol == key.F:
            self.set_fullscreen(not self.fullscreen)
            self.status_message = "Toggled fullscreen"
            return
        if symbol == key.I:
            self.current_source = (self.current_source + 1) % len(SOURCE_TYPES)
            self.config.selected_input_index = self.current_source
            self.status_message = f"Source changed to {SOURCE_TYPES[self.current_source]}"
            return
        if symbol == key.M:
            self.current_source = 2
            self.config.selected_input_index = self.current_source
            self.status_message = "Source changed to TESTMAP"
            return
        if symbol == key.S:
            self.save_config()
            return
        if symbol == key.L:
            self.load_config()
            return
        if symbol in (key._1, key._2, key._3):
            layout = {key._1: "1", key._2: "2x2", key._3: "3x3"}[symbol]
            self.active_monitor.tv_layout = layout
            self.active_monitor.tv_number = LAYOUT_TO_COUNT[layout]
            self.status_message = f"Layout changed to {layout}"
            return
        if symbol == key.UP:
            self._handle_vertical(-1 if not self.shift_pressed else 1, modifiers)
        elif symbol == key.DOWN:
            self._handle_vertical(1, modifiers)
        elif symbol == key.LEFT:
            self._handle_horizontal(-1, modifiers)
        elif symbol == key.RIGHT:
            self._handle_horizontal(1, modifiers)

    def _handle_vertical(self, direction: int, modifiers: int) -> None:
        if self.alt_pressed:
            self.grid_index = (self.grid_index + direction) % len(GRID_OPTIONS)
            self.status_message = f"Grid changed to {self.grid_size}mm"
            return
        tv = self.config.tv_mappings[self.selected_tv - 1]
        if self.shift_pressed:
            tv.height += direction * self.grid_size
            self.status_message = f"Adjusted TV {self.selected_tv} height"
        else:
            tv.y_pos += direction * self.grid_size
            self.status_message = f"Moved TV {self.selected_tv} vertically"

    def _handle_horizontal(self, direction: int, modifiers: int) -> None:
        if self.alt_pressed:
            visible = self._visible_tv_indices()
            current = visible.index(self.selected_tv) if self.selected_tv in visible else 0
            self.selected_tv = visible[(current + direction) % len(visible)]
            self.status_message = f"Selected TV {self.selected_tv}"
            return
        tv = self.config.tv_mappings[self.selected_tv - 1]
        if self.shift_pressed:
            tv.width += direction * self.grid_size
            self.status_message = f"Adjusted TV {self.selected_tv} width"
        else:
            tv.x_pos += direction * self.grid_size
            self.status_message = f"Moved TV {self.selected_tv} horizontally"

    def save_config(self) -> None:
        self.config.selected_input_index = self.current_source
        self.config.monitor_selected = min(self.config.monitor_selected, len(self.config.monitor_data) - 1)
        self.config.ensure_lengths()
        self.config_path.write_text(json.dumps(self.config.to_json(), indent=2), encoding="utf-8")
        self.status_message = f"Saved config to {self.config_path.name}"

    def load_config(self) -> None:
        self.config = AppConfig.from_json(self.config_path)
        self.current_source = self.config.selected_input_index
        self.selected_tv = min(self.selected_tv, self.config.number_tvs)
        self.status_message = f"Loaded config from {self.config_path.name}"


def main() -> None:
    window = MapperWindow()
    pyglet.app.run()


if __name__ == "__main__":
    main()
