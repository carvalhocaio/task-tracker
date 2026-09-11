"""Presentation-only formatting for tasks, using Rich for semantic-colored
terminal output. No business logic, no I/O beyond the console it's given.
"""

from rich.console import Console
from rich.table import Table

from task_tracker.domain.task import Status, Task

# One style per status, keyed by the enum itself -- this table replaces the
# fixed-width "%-12s" padding the Go version printed for every row.
STATUS_STYLES: dict[Status, str] = {
    Status.TODO: "yellow",
    Status.IN_PROGRESS: "cyan",
    Status.DONE: "green",
}

_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M"


def print_task_added(console: Console, task: Task) -> None:
    console.print(f"[green]Task added successfully (ID: {task.id})[/green]")


def print_task_updated(console: Console, task: Task) -> None:
    console.print(f"[green]Task {task.id} updated successfully[/green]")


def print_task_deleted(console: Console, task_id: int) -> None:
    console.print(f"[green]Task {task_id} deleted successfully[/green]")


def print_task_marked(console: Console, task: Task) -> None:
    console.print(
        f"[green]Task {task.id} marked as[/green] {render_status(task.status)}"
    )


def print_tasks(console: Console, tasks: list[Task]) -> None:
    if not tasks:
        console.print("[dim]No tasks found.[/dim]")
        return

    table = Table()
    table.add_column("ID", justify="right")
    table.add_column("Status")
    table.add_column("Description")
    table.add_column("Created")
    table.add_column("Updated")
    for task in tasks:
        table.add_row(
            str(task.id),
            render_status(task.status),
            task.description,
            task.created_at.strftime(_TIMESTAMP_FORMAT),
            task.updated_at.strftime(_TIMESTAMP_FORMAT),
        )
    console.print(table)


def render_status(status: Status) -> str:
    style = STATUS_STYLES[status]
    return f"[{style}]{status.value}[/{style}]"
