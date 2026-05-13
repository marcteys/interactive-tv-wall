# Code Audit — Interactive TV Wall

Audit performed 2026-05-13. All findings listed below were resolved in the same session.

---

## Findings

### A1 — Wrong return type on `pack_tv_uniforms` (Bug)

**File:** `src/tvwall/services/layout_service.py:163`

The method was annotated `-> bytes` but returned `tuple[bytes, int]`. Callers already
unpacked the tuple correctly, so no logic was wrong — the annotation was the lie.

**Resolution:** Changed annotation to `-> tuple[bytes, int]`.

---

### A2 — Stale tick interval after framerate change (Bug)

**File:** `src/tvwall/app/window.py`

`pyglet.clock.schedule_interval(self._tick, ...)` was called once at startup using the
initial `config.framerate`. If the user adjusted the framerate via the Canvas stepper,
the tick interval never updated — the source texture would keep refreshing at the old rate.

**Resolution:** Added `_reschedule_tick()` helper; called after every `handle_action` and
after load in the window so the interval always tracks the current config value.

---

### B1 — `active_monitor` property mutated config as a side effect (Design)

**File:** `src/tvwall/domain/models.py:135`

The `active_monitor` property called `self.config.ensure_lengths()` on every access,
meaning reading the property silently normalised the entire config. Properties should
not have write side effects.

**Resolution:** Removed `ensure_lengths()` from the property. Explicit calls at all
write boundaries (controller actions, load) already covered normalisation.

---

### B2 — Drawing had a hidden side effect on hit-testing (Design)

**Files:** `src/tvwall/ui/widgets.py`, `src/tvwall/ui/control_panel.py`

`WidgetPainter.draw()` called `reset()` and repopulated `self.regions` as a side effect
of rendering widgets. `hit_test()` queried those regions, making input handling silently
dependent on a prior draw pass. The contract was implicit and undocumented.

**Resolution:** Added docstrings to `WidgetPainter` and `ControlPanelView.hit_test()`
making the draw-before-hit-test contract explicit. A structural refactor (separate layout
pass) was deferred as out of scope.

---

### C1 — `assert` used for control flow in `begin_drag` (Code quality)

**File:** `src/tvwall/services/layout_service.py:133`

`assert point is not None` was used after a hit-test confirmed the point was in-rect.
Assertions are stripped under `python -O`, making this a silent failure path in
optimised mode.

**Resolution:** Replaced with an explicit `if point is None: return False` guard.

---

### C2 — Unconstrained `setattr` with raw string field names (Code quality)

**File:** `src/tvwall/services/layout_service.py:56, 63, 69`

`adjust_monitor_field`, `adjust_canvas_value`, and `adjust_tv_value` used `setattr`
with a `field_name` string received from UI payloads. An invalid or mistyped field name
would raise `AttributeError` at runtime with no useful message.

**Resolution:** Added `hasattr` guards before each `setattr`; unknown fields are silently
ignored, matching the defensive style used elsewhere in the service layer.

---

### C3 — Legacy `typing.List` import (Code quality)

**File:** `src/tvwall/domain/models.py:4`

`from typing import List` is unnecessary in Python 3.9+. `list[...]` syntax works
natively.

**Resolution:** Removed the import; replaced `List[MonitorConfig]` and `List[TVMapping]`
with `list[MonitorConfig]` and `list[TVMapping]`.

---

### D1 — Scroll had no upper bound (UX)

**File:** `src/tvwall/ui/control_panel.py`

`scroll_offset` was clamped at a minimum of `0.0` but had no maximum. A user could
scroll far past all TV items, leaving the panel blank with no way to know they needed
to scroll back.

**Resolution:** `draw()` now computes `max_scroll` from the total TV content height
and stores it. `scroll()` accepts an optional `max_offset` parameter and clamps the
offset to `[0, max_offset]`. `window.py` passes `panel.max_scroll` on each scroll event.

---

## Deferred

### E1 — pyglet objects created every draw frame (Performance)

**Files:** `src/tvwall/ui/widgets.py`, `src/tvwall/rendering/map_preview_renderer.py`,
`src/tvwall/app/window.py:51-57`

All `pyglet.text.Label` and `pyglet.shapes.BorderedRectangle` objects are allocated
fresh on every frame. At 30 fps with a full panel this is hundreds of heap allocations
per second. The fix (pyglet `Batch` + reusable shape/label objects) is correct but
larger in scope and was deferred to avoid scope creep.

**Recommended fix:** Introduce a `pyglet.graphics.Batch` in `WidgetPainter` and
`MapPreviewRenderer`; accumulate shapes into the batch during `draw()` and call
`batch.draw()` once per frame.
