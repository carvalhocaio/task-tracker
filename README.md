# Task Tracker CLI

A simple command-line to-do list manager, built with Go's standard library only - no
external dependencies. Solution for the [roadmap.sh Task Tracker project](https://roadmap.sh/projects/task-tracker).

## build

```bash
go build -o task-cli .
```

## usage

```bash
# add a new task
./task-cli add "Buy groceries"
# task added successfully (ID: 1)

# update a task's description
./task-cli update 1 "Buy groceries and cook dinner"

# delete a task
./task-cli delete 1

# mark a task's status
./task-cli mark-in-progress 1
./task-cli mark-done 1

# list tasks
./task-cli list                 # all tasks
./task-cli list done            # only done
./task-cli list todo            # only todo
./task-cli list in-progress     # only in-progress
```

## design

The project is split into four packages, each with a single responsibility:

package            | responsibility
-------------------|------------------------------------------------------------
`internal/task`    | the `Task` entity and its status rules.
`internal/storage` | reads/writes `tasks.json`. Knows nothing about CLI or rules
`internal/app`     | business logic (add/update/delete/status/list)
`internal/cli`     | parses `os.Args`, calls `app`, formats terminal output.

This separation means `internal/app` can be unit tested without touching the filesystem,
and the storage format could be swapped (e.g. for SQLite) without touching business
logic.

## data file

Tasks are stored in `tasks.json` in the current working directory. The file is created
automatically the first time a task is added - `list` on a missing file simply reports no
tasks, without writing anything to disk.

## known limitations

- ID assignment (`max(id) + 1`) assumes a single process writing at a time. Fine for local CLI use; not safe for concurrent writes.
- No pagination or sorting flags on `list` - tasks are returned in file order.
