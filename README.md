# Task Tracker

![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![uv](https://img.shields.io/badge/packaging-uv-de5fe9)
![pytest](https://img.shields.io/badge/tests-pytest-0a9edc)
![Ruff](https://img.shields.io/badge/lint%2Fformat-ruff-d7ff64)
![Rich](https://img.shields.io/badge/output-rich-ff69b4)

A command-line to-do list manager — add tasks, move them through
`todo → in-progress → done`, and list them filtered by status. Everything
lives in a single plain JSON file you can open and edit by hand.

## Table of contents

- [Features](#features)
- [Requirements](#requirements)
- [Usage](#usage)
- [Development](#development)
- [Project structure](#project-structure)
- [Design notes](#design-notes)
- [Project origin](#project-origin)

## Features

- Add, update, delete and list tasks, with optional status filtering
- Three-state lifecycle: `todo`, `in-progress`, `done`
- Local persistence via a plain JSON file (`tasks.json`), created on first add
- Every task carries `createdAt` / `updatedAt` timestamps, refreshed on change
- Semantic-colored terminal output (Rich): a table for `list`, green for
  success, red for errors

| Command            | Description                            |
|--------------------|----------------------------------------|
| `add`              | Add a new task                         |
| `update`           | Change a task's description            |
| `delete`           | Delete a task by id                    |
| `mark-in-progress` | Mark a task as in-progress             |
| `mark-done`        | Mark a task as done                    |
| `list`             | List tasks, optionally filtered by status |

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Usage

```bash
git clone https://github.com/carvalhocaio/task-tracker.git
cd task-tracker
uv run task-cli <COMMAND> [ARGS]
```

![demo](assets/demo.gif)

> The GIF above is generated with [VHS](https://github.com/charmbracelet/vhs)
> from [`assets/demo.tape`](assets/demo.tape). Regenerate it locally with
> `vhs assets/demo.tape` (requires VHS <= 0.11.0 -- 0.12.0 has a rendering
> regression that silently produces no output).

### Commands

**Add a task**
```bash
uv run task-cli add "Buy groceries"
# Task added successfully (ID: 1)
```
New tasks always start in `todo`.

**Update a task's description**
```bash
uv run task-cli update 1 "Buy groceries and cook dinner"
```

**Delete a task**
```bash
uv run task-cli delete 1
```

**Mark a task's status**
```bash
uv run task-cli mark-in-progress 1
uv run task-cli mark-done 1
```

**List tasks** (optionally filtered by status)
```bash
uv run task-cli list
uv run task-cli list todo
uv run task-cli list in-progress
uv run task-cli list done
```

Commands exit `0` on success and `1` on an application error (unknown id,
blank description, unreadable file); argparse rejects malformed arguments
with its own `2`.

## Development

```bash
uv sync                    # install runtime + dev dependencies
uv run pytest -v           # run tests
uv run ruff check .        # lint
uv run ruff format .       # format
```

Or the equivalent `make` shortcuts:

```bash
make sync
make test
make lint
make format
make check   # lint + format-check + test, the aggregate gate
```

## Project structure

```
src/task_tracker/
├── __main__.py                # composition root -- all wiring happens here
├── errors.py                  # AppError hierarchy, shared across layers
├── domain/                    # pure models: no I/O, no persistence
│   └── task.py                 # Task, Status
├── application/               # use-case orchestration
│   └── task_service.py         # TaskService
└── infrastructure/
    ├── repository.py           # TaskRepository Protocol (the port)
    ├── json_repository.py       # JsonRepository (the adapter)
    └── cli/
        ├── parser.py            # argparse subcommand definitions
        ├── output.py             # Rich-based table/status formatting
        └── session.py            # dispatch loop, the only layer touching the console
```

## Design notes

Dependencies point inward: `cli → application → domain`, and `domain` depends
on nothing. `TaskService` depends on the `TaskRepository` Protocol in
`infrastructure/repository.py`, not on the JSON file directly, so tests
exercise it against an in-memory fake repository while
`infrastructure/json_repository.py` is tested separately against real
temporary files — swapping in SQLite later would mean writing one new adapter
and changing no business logic.

Timestamps are passed *into* the repository rather than read from the clock
there, and `TaskService` takes an injectable `clock`. That is what lets the
suite assert that `updated_at` moves while `created_at` doesn't, without
sleeping. Rich is used only in the `infrastructure/cli` layer, for
presentation; it has no influence on the domain or application logic.

`tasks.json` keeps the exact on-disk shape the original Go version wrote —
a flat array with `createdAt` / `updatedAt` keys — so an existing file still
loads. Writes go through a temporary file and `os.replace`, so an interrupted
write leaves the previous file intact instead of a truncated one.

### Known limitations

- Every mutation rewrites the whole file, and ids are allocated as
  `max(id) + 1`. Both assume a single process writing at a time — fine for a
  local CLI, not safe for concurrent writers.
- Because ids come from `max(id) + 1` over the surviving tasks, deleting the
  newest task frees its id for the next `add`. Keeping `tasks.json` a plain,
  hand-editable array is worth more here than gapless ids.
- No pagination or sorting flags on `list` — tasks are returned by id.

## Project origin

Built as an implementation of the
[Task Tracker](https://roadmap.sh/projects/task-tracker) project from
[roadmap.sh](https://roadmap.sh), originally written in Go and rewritten in
Python.
