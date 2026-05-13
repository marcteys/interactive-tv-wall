# PLAN

## Scope

Refactor the Python port into a modular, class-based `pyglet + moderngl` application with a friendlier in-window control surface, stronger state handling, disk-based shader loading, and automated tests.

## Milestones

- [x] Milestone 1 - Establish architecture and tracking
  - Acceptance note: the app entrypoint is thin, config/state logic moved into package modules, and the plan is tracked here.
- [x] Milestone 2 - Rendering cleanup and GPU pipeline hardening
  - Acceptance note: shaders load from disk, output rendering is isolated, and TV uniform packing is testable.
- [x] Milestone 3 - Friendly control panel and app workflow
  - Acceptance note: a structured `pyglet` control panel replaces the old text-only workflow and exposes monitor/canvas/TV editing.
- [x] Milestone 4 - Robustness and state invariants
  - Acceptance note: normalization, selection fallback, and hit-testing behavior are centralized in the model/service layer.
- [x] Milestone 5 - Automated tests and smoke coverage
  - Acceptance note: `pytest` now covers config normalization, repository round-trips, layout math, controller flows, source generation, and viewport/shader loading seams.
- [x] Milestone 6 - Final validation and documentation refresh
  - Acceptance note: docs, TODOs, and run/test commands now reflect the modular architecture and current scope.

## Architecture

- `src/tvwall/domain/`: config, state, constants, and geometry
- `src/tvwall/services/`: config I/O, source generation, layout/edit math
- `src/tvwall/rendering/`: shader loading, output rendering, map preview, viewport layout
- `src/tvwall/ui/`: reusable widget painter and control panel view
- `src/tvwall/app/`: controller, window bridge, and application entrypoint

## Follow-up notes discovered during implementation

- The current pass intentionally keeps monitor editing in a single window, even though the original openFrameworks app can spawn true extra output windows.
- Source support still focuses on testcards plus generated map-test content; camera and NDI remain deferred.
