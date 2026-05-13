# Translate this openFrameworks project to Python

Translate the current openFrameworks project or selected openFrameworks code into a complete Python project.

Follow the repository instructions in `convertor/.github/copilot-instructions.md`.

## Required process

1. Inspect the current workspace and identify openFrameworks files, especially `src/ofApp.h`, `src/ofApp.cpp`, `src/main.cpp`, `addons.make`, `config.make`, shader files, and assets.
2. Run or emulate the project inventory step:

```bash
python convertor/scripts/analyze_of_project.py . --output convertor/of_project_inventory.json
```

3. Classify the project type and choose the Python target stack using `convertor/docs/framework-selection.md`.
4. Generate the complete Python port at the repository root.
5. Include all mandatory files:

```text
README.md
requirements.txt
MIGRATION.md
TODO.md
src/main.py
```

6. Copy or reference assets under `assets/`.
7. Run or emulate validation:

```bash
python convertor/scripts/validate_python_project.py .
```

8. Fix validation issues or document why they cannot be fixed automatically.

## Output constraints

- Do not only explain. Create or edit files.
- Do not omit documentation.
- Do not claim full equivalence when unresolved rendering, hardware, audio, shader, or addon behavior remains.
- Prefer a minimal working Python app plus clear TODOs over a large incomplete translation.
