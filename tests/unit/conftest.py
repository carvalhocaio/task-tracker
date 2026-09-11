"""Shared test fixtures."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from task_tracker.domain.task import Status, Task
from task_tracker.errors import TaskNotFoundError

EPOCH = datetime(2026, 9, 11, 12, 0, tzinfo=UTC)


class FakeTaskRepository:
    """In-memory stand-in for TaskRepository -- lets TaskService be
    unit-tested without touching the filesystem."""

    def __init__(self) -> None:
        self._rows: dict[int, Task] = {}
        self._next_id = 1

    def add(self, description: str, created_at: datetime) -> Task:
        task_id = self._next_id
        self._next_id += 1
        task = Task(
            id=task_id,
            description=description,
            status=Status.TODO,
            created_at=created_at,
            updated_at=created_at,
        )
        self._rows[task_id] = task
        return task

    def update(
        self,
        task_id: int,
        description: str | None,
        status: Status | None,
        updated_at: datetime,
    ) -> Task:
        task = self._rows.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)

        changes: dict[str, object] = {"updated_at": updated_at}
        if description is not None:
            changes["description"] = description
        if status is not None:
            changes["status"] = status
        updated = replace(task, **changes)
        self._rows[task_id] = updated
        return updated

    def delete(self, task_id: int) -> None:
        if task_id not in self._rows:
            raise TaskNotFoundError(task_id)
        del self._rows[task_id]

    def list(self, status: Status | None = None) -> list[Task]:
        tasks = self._rows.values()
        if status is not None:
            tasks = (task for task in tasks if task.status is status)
        return sorted(tasks, key=lambda task: task.id)


class FixedClock:
    """Deterministic clock: every call advances by one minute, so tests can
    assert that updated_at moved without sleeping."""

    def __init__(self, start: datetime = EPOCH) -> None:
        self._now = start

    def __call__(self) -> datetime:
        now = self._now
        self._now += timedelta(minutes=1)
        return now


@pytest.fixture
def fake_repository() -> FakeTaskRepository:
    return FakeTaskRepository()


@pytest.fixture
def fixed_clock() -> FixedClock:
    return FixedClock()
