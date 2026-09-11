"""JSON file adapter for TaskRepository. Uses stdlib json only -- the
roadmap.sh brief calls for a plain JSON file, and the on-disk shape is
kept byte-compatible with the Go version (camelCase keys, ISO-8601
timestamps) so an existing tasks.json still loads.

Every mutation is a load -> change -> save cycle. That is fine for a
local single-process CLI and is the same trade-off the Go version made;
it is not safe for concurrent writers.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime

from task_tracker.domain.task import Status, Task
from task_tracker.errors import CorruptDataError, StorageError, TaskNotFoundError

_ID = "id"
_DESCRIPTION = "description"
_STATUS = "status"
_CREATED_AT = "createdAt"
_UPDATED_AT = "updatedAt"


class JsonRepository:
    def __init__(self, path: str) -> None:
        self._path = path

    def add(self, description: str, created_at: datetime) -> Task:
        tasks = self._load()
        task = Task(
            id=_next_id(tasks),
            description=description,
            status=Status.TODO,
            created_at=created_at,
            updated_at=created_at,
        )
        tasks.append(task)
        self._save(tasks)
        return task

    def update(
        self,
        task_id: int,
        description: str | None,
        status: Status | None,
        updated_at: datetime,
    ) -> Task:
        tasks = self._load()
        index = _index_of(tasks, task_id)
        current = tasks[index]
        updated = Task(
            id=current.id,
            description=description if description is not None else current.description,
            status=status if status is not None else current.status,
            created_at=current.created_at,
            updated_at=updated_at,
        )
        tasks[index] = updated
        self._save(tasks)
        return updated

    def delete(self, task_id: int) -> None:
        tasks = self._load()
        del tasks[_index_of(tasks, task_id)]
        self._save(tasks)

    def list(self, status: Status | None = None) -> list[Task]:
        tasks = self._load()
        if status is not None:
            tasks = [task for task in tasks if task.status is status]
        return sorted(tasks, key=lambda task: task.id)

    def _load(self) -> list[Task]:
        """Reads every task from disk. A missing file reads as empty and is
        left untouched -- it is created lazily on the first write."""
        try:
            with open(self._path, encoding="utf-8") as handle:
                content = handle.read()
        except FileNotFoundError:
            return []
        except OSError as error:
            raise StorageError(error) from error

        if not content.strip():
            return []

        try:
            records = json.loads(content)
        except json.JSONDecodeError as error:
            raise CorruptDataError(error) from error

        if not isinstance(records, list):
            raise CorruptDataError(
                TypeError(f"{self._path} should hold a list of tasks")
            )
        return [_to_task(record) for record in records]

    def _save(self, tasks: list[Task]) -> None:
        """Writes the full list back atomically: a crash mid-write leaves
        the previous file intact rather than a truncated one."""
        payload = json.dumps([_to_record(task) for task in tasks], indent=2)
        directory = os.path.dirname(os.path.abspath(self._path))
        try:
            with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", dir=directory, delete=False
            ) as handle:
                handle.write(payload)
                temporary_path = handle.name
            os.replace(temporary_path, self._path)
        except OSError as error:
            raise StorageError(error) from error


def _to_record(task: Task) -> dict:
    return {
        _ID: task.id,
        _DESCRIPTION: task.description,
        _STATUS: task.status.value,
        _CREATED_AT: task.created_at.isoformat(),
        _UPDATED_AT: task.updated_at.isoformat(),
    }


def _to_task(record: object) -> Task:
    if not isinstance(record, dict):
        raise CorruptDataError(TypeError(f"expected a task object, got {type(record)}"))
    try:
        return Task(
            id=record[_ID],
            description=record[_DESCRIPTION],
            status=Status(record[_STATUS]),
            created_at=_to_datetime(record[_CREATED_AT]),
            updated_at=_to_datetime(record[_UPDATED_AT]),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise CorruptDataError(error) from error


def _to_datetime(value: str) -> datetime:
    """Parses an ISO-8601 timestamp. Go writes UTC as a trailing "Z", which
    fromisoformat only accepts from 3.11 onwards -- normalised anyway so the
    intent is explicit."""
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _next_id(tasks: list[Task]) -> int:
    """max(id) + 1, so a deleted id is never handed out again. This lives in
    the adapter because id allocation is a persistence concern -- a SQLite
    adapter would delegate it to AUTOINCREMENT."""
    return max((task.id for task in tasks), default=0) + 1


def _index_of(tasks: list[Task], task_id: int) -> int:
    for index, task in enumerate(tasks):
        if task.id == task_id:
            return index
    raise TaskNotFoundError(task_id)
