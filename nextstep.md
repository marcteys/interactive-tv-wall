# Next Step

## Current assessment

The recent changes moved the code in the right direction:

- removing mutation from `active_monitor`
- bounding panel scroll
- replacing the `assert` in drag startup
- adding guards around dynamic field updates

The current automated checks are still clean:

- `pytest`: passing
- validation: passing
- Python compile pass: passing

That said, for an app that needs to run for days nonstop, the biggest remaining concerns are now long-run frame stability, allocation pressure, and fault tolerance rather than basic correctness.

## Highest-priority findings

### 1. Per-frame `pyglet` object churn is still the biggest performance risk

Fresh `pyglet.text.Label` and `pyglet.shapes.BorderedRectangle` objects are created every frame in:

- `src/tvwall/ui/widgets.py`
- `src/tvwall/ui/control_panel.py`
- `src/tvwall/rendering/map_preview_renderer.py`
- `src/tvwall/app/window.py`

This likely will not leak memory outright, but over days of uptime it is exactly the sort of constant allocation pattern that causes GC jitter and inconsistent frame pacing.

**Priority:** highest

**Recommended fix:** introduce `pyglet.graphics.Batch` and reusable label/shape objects for UI and map preview rendering.

### 2. Source regeneration is still expensive during live editing

When source state changes, especially in `TESTMAP` mode:

- a full PIL image is rebuilt
- the texture is re-uploaded to the GPU

This happens through:

- `src/tvwall/services/source_service.py`
- `src/tvwall/rendering/output_renderer.py`

During drag/resize interactions, this can create visible CPU and upload spikes.

**Priority:** very high

**Recommended fix:**

- cache resized testcards by source and resolution
- rebuild `TESTMAP` only when mapping data actually changes
- reduce unnecessary full texture uploads where possible

### 3. Config save is not crash-safe yet

`config.json` is written directly in:

- `src/tvwall/services/config_repository.py`

If the process is interrupted during save, the config can be left truncated or corrupted.

**Priority:** high

**Recommended fix:** use atomic save semantics:

1. write to a temp file
2. flush/sync if needed
3. replace the original file

### 4. There is still no fault containment around runtime boundaries

A single unexpected exception in:

- draw
- tick/update
- save/load
- shader/image handling

can still terminate the app process.

**Priority:** high

**Recommended fix:**

- add structured logging
- wrap draw/tick/save/load boundaries in defensive exception handling
- degrade gracefully when possible instead of crashing hard

### 5. Tick rescheduling is broader than necessary

`_reschedule_tick()` is correct, but it is currently called after several actions that do not actually change framerate.

This is not a correctness bug, but it adds avoidable scheduler churn.

**Priority:** medium

**Recommended fix:** only reschedule when framerate actually changes.

## Recommended next focus

The next implementation pass should be a dedicated **runtime hardening** pass with this scope:

### 1. Batch and reuse UI draw objects

- add `pyglet.graphics.Batch`
- reuse labels and shapes instead of allocating them every frame
- target stable frame times and lower GC pressure

### 2. Reduce image rebuild and texture upload pressure

- cache resized testcards
- only rebuild `TESTMAP` when necessary
- avoid redundant full-frame texture updates during editing

### 3. Make config persistence crash-safe

- atomic save
- optional backup or last-good config strategy

### 4. Add unattended-runtime safeguards

- structured log file
- guarded draw/tick/save/load boundaries
- status fallback on recoverable failures
- optional periodic heartbeat logging

## Suggested measurement pass

Before deeper GL work, add lightweight instrumentation for:

- source rebuild time
- texture upload time
- UI draw time
- total frame time

That will tell us whether the next real bottleneck is:

- PIL image generation
- `pyglet` allocation churn
- texture upload bandwidth
- or something else

## Short version

If this needs to run for days nonstop, the best next work is:

1. reusable/batched UI drawing
2. cached source images and fewer texture uploads
3. atomic config saves
4. logging and exception containment

That is the highest-value path for both performance and stability.
