"""Persistence port: everything the application layer needs from storage,
and nothing more. TaskService depends on this Protocol, not on the JSON
file directly -- swapping the backend later (SQLite, say) means writing a
new adapter, with zero changes to business logic.

Timestamps are passed in rather than read from the clock here, so the
adapter stays free of time and stays trivially testable.
"""

from datetime import datetime
from typing import Protocol

from task_tracker.domain.task import Status, Task


class TaskRepository(Protocol):
    def add(self, description: str, created_at: datetime) -> Task: ...

    def update(
        self,
        task_id: int,
        description: str | None,
        status: Status | None,
        updated_at: datetime,
    ) -> Task: ...

    def delete(self, task_id: int) -> None: ...

    def list(self, status: Status | None = None) -> list[Task]: ...
