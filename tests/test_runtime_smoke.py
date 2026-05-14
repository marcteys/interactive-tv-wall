from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_window_live_smoke() -> None:
    root = Path(__file__).resolve().parents[1]
    script = """
import sys
from pathlib import Path
sys.path.insert(0, 'src')
from tvwall.app.window import MapperWindow
import pyglet
w = MapperWindow(Path('.').resolve())
w.controller.state.show_framerate = True
pyglet.clock.schedule_once(lambda dt: (w.dispatch_event('on_draw'), w.close(), pyglet.app.exit()), 0.1)
pyglet.app.run()
print('window-live-smoke-ok')
"""
    result = subprocess.run(
        [str(root / ".venv" / "Scripts" / "python.exe"), "-c", script],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "window-live-smoke-ok" in result.stdout
