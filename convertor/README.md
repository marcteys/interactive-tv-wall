# Converter Pack

This folder contains the prompt pack and helper files that were used to translate the original openFrameworks project into the Python app now living at the repository root.

Contents:

- `.copilot/`: reusable prompts
- `.github/`: repository instructions for the translation workflow
- `.vscode/`: VS Code tasks/settings for analysis, validation, and running
- `docs/`: framework-selection and output guidance
- `scripts/`: project analysis and validation helpers
- `templates/`: starter Python-port templates
- `of_project_inventory.json`: the analyzed inventory from the source project

The generated app itself is no longer under `python_port/`; it now lives at the root with `src/`, `assets/`, `README.md`, `requirements.txt`, `MIGRATION.md`, `TODO.md`, and `config.json`.
