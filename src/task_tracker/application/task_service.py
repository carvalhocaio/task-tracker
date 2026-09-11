"""Orchestrates task use cases (add/update/delete/set-status/list), wiring
validation rules to the TaskRepository port. Knows nothing about JSON or
the terminal.
"""

from collections.abc import Callable
from datetime import UTC, datetime

from task_tracker.domain.task import Status, Task
from task_tracker.errors import EmptyDescriptionError
from task_tracker.infrastructure.repository import TaskRepository

Clock = Callable[[], datetime]


def _utc_now() -> datetime:
    return datetime.now(UTC)


class TaskService:
    def __init__(self, repository: TaskRepository, clock: Clock = _utc_now) -> None:
        self._repository = repository
        self._clock = clock

    def add(self, description: str) -> Task:
        """Creates a task in status "todo". Raises EmptyDescriptionError if
        the description is blank.
        """
        return self._repository.add(_require_description(description), self._clock())

    def update(self, task_id: int, description: str) -> Task:
        """Changes a task's description and refreshes updated_at. Raises
        TaskNotFoundError (propagated from the repository) if task_id
        doesn't exist.
        """
        return self._repository.update(
            task_id,
            description=_require_description(description),
            status=None,
            updated_at=self._clock(),
        )

    def delete(self, task_id: int) -> None:
        """Raises TaskNotFoundError (from the repository) if missing."""
        self._repository.delete(task_id)

    def set_status(self, task_id: int, status: Status) -> Task:
        """Moves a task to `status` and refreshes updated_at."""
        return self._repository.update(
            task_id, description=None, status=status, updated_at=self._clock()
        )

    def list(self, status: Status | None = None) -> list[Task]:
        return self._repository.list(status)


def _require_description(description: str) -> str:
    """Trims a description and rejects blank input. The Go version only
    compared against "", so `add "   "` created a whitespace task."""
    stripped = description.strip()
    if not stripped:
        raise EmptyDescriptionError
    return stripped
