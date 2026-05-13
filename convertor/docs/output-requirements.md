# Output requirements for generated Python ports

The AI agent must generate a complete Python app at the repository root.

## Required files

```text
./
  README.md
  requirements.txt
  MIGRATION.md
  TODO.md
  src/
    main.py
  assets/
```

## README.md template

```markdown
# [Project name] Python Port

## Overview
[What this project does.]

## Selected Python stack
[Framework and dependencies, with rationale.]

## Installation
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

## Run
python src/main.py

## Assets
[Explain copied or required assets.]

## Known limitations
[Summarize unresolved behavior.]
```

## MIGRATION.md template

```markdown
# Migration Notes

## Source files inspected
- [file]

## openFrameworks features detected
- [feature]

## Framework decision
Chosen: [stack]
Rejected alternatives: [why]

## API mapping
| openFrameworks | Python |
|---|---|
| [symbol] | [translation] |

## Behavioral notes
[Timing, rendering, input, assets, devices, shaders.]

## Manual migration items
[Anything requiring human review.]
```

## TODO.md template

```markdown
# TODO

## high
- [ ] [Specific unresolved behavior, original file/symbol, reason.]

## medium
- [ ] [Improvement or fidelity issue.]

## low
- [ ] [Cleanup or optional enhancement.]
```
