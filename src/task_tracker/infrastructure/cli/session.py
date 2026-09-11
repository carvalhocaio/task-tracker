"""Drives one CLI invocation: parses argv, dispatches to TaskService, and
prints results or errors. The only layer that touches the console for
command output (formatting itself is delegated to output.py).
"""

import argparse

from rich.console import Console

from task_tracker.application.task_service import TaskService
from task_tracker.domain.task import Status
from task_tracker.errors import AppError
from task_tracker.infrastructure.cli import output
from task_tracker.infrastructure.cli.parser import (
    MARKABLE_STATUSES,
    build_parser,
    mark_command,
)

# Reverse of parser.mark_command: "mark-done" -> Status.DONE. Built from the
# same tuple the parser registers, so a new markable status needs one edit,
# not two.
_MARK_COMMANDS = {mark_command(status): status for status in MARKABLE_STATUSES}


class Session:
    def __init__(
        self,
        service: TaskService,
        console: Console | None = None,
        error_console: Console | None = None,
    ) -> None:
        self._service = service
        self._console = console if console is not None else Console()
        self._error_console = (
            error_console if error_console is not None else Console(stderr=True)
        )

    def run(self, argv: list[str]) -> int:
        args = build_parser().parse_args(argv)
        try:
            self._dispatch(args)
        except AppError as error:
            self._error_console.print(f"[bold red]Error:[/bold red] {error}")
            return 1
        return 0

    def _dispatch(self, args: argparse.Namespace) -> None:
        if args.command in _MARK_COMMANDS:
            task = self._service.set_status(args.id, _MARK_COMMANDS[args.command])
            output.print_task_marked(self._console, task)
            return

        match args.command:
            case "add":
                output.print_task_added(
                    self._console, self._service.add(args.description)
                )
            case "update":
                output.print_task_updated(
                    self._console, self._service.update(args.id, args.description)
                )
            case "delete":
                self._service.delete(args.id)
                output.print_task_deleted(self._console, args.id)
            case "list":
                status = Status.parse(args.status) if args.status else None
                output.print_tasks(self._console, self._service.list(status))
