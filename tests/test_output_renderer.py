from __future__ import annotations

from tvwall.rendering.output_renderer import OutputRenderer


class FakeUniform:
    def __init__(self) -> None:
        self.writes: list[bytes] = []

    def write(self, data: bytes) -> None:
        self.writes.append(data)


class FakeProgram:
    def __init__(self) -> None:
        self.values: dict[str, object] = {}
        self.uniforms = {"u_tex0": FakeUniform(), "u_tvdata": FakeUniform()}

    def __setitem__(self, key: str, value: object) -> None:
        if key not in self.uniforms:
            raise KeyError(key)
        self.values[key] = value

    def __getitem__(self, key: str) -> FakeUniform:
        if key not in self.uniforms:
            raise KeyError(key)
        return self.uniforms[key]


class FakeScreen:
    def __init__(self) -> None:
        self.use_calls = 0

    def use(self) -> None:
        self.use_calls += 1


class FakeContext:
    def __init__(self) -> None:
        self.screen = FakeScreen()
        self.disabled: list[int] = []
        self.enabled: list[int] = []

    def disable(self, flag: int) -> None:
        self.disabled.append(flag)

    def enable(self, flag: int) -> None:
        self.enabled.append(flag)


def test_set_uniform_skips_missing_members() -> None:
    program = FakeProgram()
    assert OutputRenderer._set_uniform(program, "u_tex0", 0) is True
    assert OutputRenderer._set_uniform(program, "u_tv_count", 3) is False
    assert program.values == {"u_tex0": 0}


def test_write_uniform_skips_missing_members() -> None:
    program = FakeProgram()
    payload = b"hello"
    assert OutputRenderer._write_uniform(program, "u_tvdata", payload) is True
    assert OutputRenderer._write_uniform(program, "u_canvas", payload) is False
    assert program.uniforms["u_tvdata"].writes == [payload]


def test_configure_draw_state_resets_default_framebuffer() -> None:
    renderer = OutputRenderer.__new__(OutputRenderer)
    renderer.ctx = FakeContext()
    renderer._configure_draw_state()
    assert renderer.ctx.screen.use_calls == 1
    assert renderer.ctx.disabled
    assert renderer.ctx.enabled
