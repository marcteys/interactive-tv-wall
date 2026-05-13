from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

import pyglet

from tvwall.app.window import MapperWindow


def configure_logging(project_root: Path) -> None:
    logger = logging.getLogger("tvwall")
    if logger.handlers:
        return
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(project_root / "tvwall.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(handler)


def main() -> None:
    project_root = Path(__file__).resolve().parents[3]
    configure_logging(project_root)
    MapperWindow(project_root)
    pyglet.app.run()
