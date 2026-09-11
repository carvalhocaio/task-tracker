"""Builds the argparse CLI surface: the six positional subcommands the
roadmap.sh brief defines (add, update, delete, mark-in-progress,
mark-done, list).
"""

import argparse

from task_tracker.domain.task import Status

# The two forward transitions the brief exposes as commands; each one
# becomes `mark-<status>`. Driving them off Status keeps the command names,
# the help text and the dispatch in session.py from drifting apart.
MARKABLE_STATUSES: tuple[Status, ...] = (Status.IN_PROGRESS, Status.DONE)


def mark_command(status: Status) -> str:
    return f"mark-{status.value}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="task-cli",
        description="Track your to-do list from the command line",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add = subparsers.add_parser("add", help="Add a new task")
    add.add_argument("description", help="What needs doing")

    update = subparsers.add_parser("update", help="Update a task's description")
    update.add_argument("id", type=int, help="Id of the task to update")
    update.add_argument("description", help="The new description")

    delete = subparsers.add_parser("delete", help="Delete a task by id")
    delete.add_argument("id", type=int, help="Id of the task to delete")

    for status in MARKABLE_STATUSES:
        mark = subparsers.add_parser(
            mark_command(status), help=f"Mark a task as {status.value}"
        )
        mark.add_argument("id", type=int, help="Id of the task to mark")

    list_cmd = subparsers.add_parser("list", help="List tasks")
    list_cmd.add_argument(
        "status",
        nargs="?",
        default=None,
        choices=Status.values(),
        help="Only show tasks with this status (default: all)",
    )

    return parser
