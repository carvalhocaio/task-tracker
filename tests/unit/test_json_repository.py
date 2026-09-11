"""Tests for JsonRepository, exercised against real files under tmp_path
-- the one place in the suite that touches the filesystem."""

import json
from datetime import UTC, datetime

import pytest

from task_tracker.domain.task import Status
from task_tracker.errors import CorruptDataError, TaskNotFoundError
from task_tracker.infrastructure.json_repository import JsonRepository

NOW = datetime(2026, 9, 11, 12, 0, tzinfo=UTC)
LATER = datetime(2026, 9, 11, 13, 30, tzinfo=UTC)

# Exactly what the Go version wrote: camelCase keys, RFC 3339 timestamps.
GO_FORMAT_FILE = json.dumps(
    [
        {
            "id": 1,
            "description": "Buy groceries",
            "status": "todo",
            "createdAt": "2026-09-11T12:00:00Z",
            "updatedAt": "2026-09-11T12:00:00Z",
        }
    ]
)


@pytest.fixture
def path(tmp_path):
    return tmp_path / "tasks.json"


@pytest.fixture
def repository(path):
    return JsonRepository(str(path))


class TestLoad:
    def test_missing_file_reads_as_empty(self, repository):
        assert repository.list() == []

    def test_missing_file_is_not_created_by_a_read(self, repository, path):
        repository.list()

        assert not path.exists()

    def test_empty_file_reads_as_empty(self, repository, path):
        path.write_text("", encoding="utf-8")

        assert repository.list() == []

    def test_reads_a_file_written_by_the_go_version(self, repository, path):
        path.write_text(GO_FORMAT_FILE, encoding="utf-8")

        [task] = repository.list()
        assert task.id == 1
        assert task.description == "Buy groceries"
        assert task.status is Status.TODO
        assert task.created_at == NOW

    @pytest.mark.parametrize(
        "content",
        [
            "{not json",
            '{"id": 1}',
            '[{"id": 1, "description": "x"}]',
            '[{"id": 1, "description": "x", "status": "bogus",'
            ' "createdAt": "2026-09-11T12:00:00Z",'
            ' "updatedAt": "2026-09-11T12:00:00Z"}]',
            '[{"id": 1, "description": "x", "status": "todo",'
            ' "createdAt": "not-a-date", "updatedAt": "2026-09-11T12:00:00Z"}]',
        ],
        ids=["invalid-json", "not-a-list", "missing-field", "bad-status", "bad-date"],
    )
    def test_rejects_corrupt_content(self, repository, path, content):
        path.write_text(content, encoding="utf-8")

        with pytest.raises(CorruptDataError):
            repository.list()


class TestAdd:
    def test_creates_the_file_on_first_write(self, repository, path):
        repository.add("Buy groceries", NOW)

        assert path.exists()

    def test_first_task_gets_id_one(self, repository):
        assert repository.add("Buy groceries", NOW).id == 1

    def test_ids_increment(self, repository):
        repository.add("Buy groceries", NOW)

        assert repository.add("Cook dinner", NOW).id == 2

    def test_reuses_the_highest_id_once_it_is_deleted(self, repository):
        """max(id) + 1 over a bare JSON array means deleting the newest task
        frees its id. Documented rather than fixed: keeping tasks.json a
        plain, hand-editable array is worth more here than gapless ids."""
        repository.add("Buy groceries", NOW)
        second = repository.add("Cook dinner", NOW)
        repository.delete(second.id)

        assert repository.add("Walk the dog", NOW).id == 2

    def test_keeps_ids_stable_when_an_older_task_is_deleted(self, repository):
        first = repository.add("Buy groceries", NOW)
        repository.add("Cook dinner", NOW)
        repository.delete(first.id)

        assert repository.add("Walk the dog", NOW).id == 3

    def test_persists_across_instances(self, repository, path):
        repository.add("Buy groceries", NOW)

        [task] = JsonRepository(str(path)).list()
        assert task.description == "Buy groceries"

    def test_round_trips_timestamps(self, repository, path):
        repository.add("Buy groceries", NOW)

        [task] = JsonRepository(str(path)).list()
        assert task.created_at == NOW
        assert task.updated_at == NOW

    def test_writes_the_go_compatible_key_names(self, repository, path):
        repository.add("Buy groceries", NOW)

        [record] = json.loads(path.read_text(encoding="utf-8"))
        assert set(record) == {
            "id",
            "description",
            "status",
            "createdAt",
            "updatedAt",
        }


class TestUpdate:
    def test_changes_only_the_given_fields(self, repository):
        task = repository.add("Buy groceries", NOW)

        updated = repository.update(
            task.id, description="Cook dinner", status=None, updated_at=LATER
        )

        assert updated.description == "Cook dinner"
        assert updated.status is Status.TODO
        assert updated.created_at == NOW
        assert updated.updated_at == LATER

    def test_changes_the_status(self, repository):
        task = repository.add("Buy groceries", NOW)

        updated = repository.update(
            task.id, description=None, status=Status.DONE, updated_at=LATER
        )

        assert updated.status is Status.DONE
        assert updated.description == "Buy groceries"

    def test_persists_the_change(self, repository, path):
        task = repository.add("Buy groceries", NOW)

        repository.update(
            task.id, description=None, status=Status.DONE, updated_at=LATER
        )

        [reloaded] = JsonRepository(str(path)).list()
        assert reloaded.status is Status.DONE

    def test_raises_not_found_for_an_unknown_id(self, repository):
        with pytest.raises(TaskNotFoundError):
            repository.update(99, description="x", status=None, updated_at=LATER)


class TestDelete:
    def test_removes_the_task(self, repository):
        task = repository.add("Buy groceries", NOW)

        repository.delete(task.id)

        assert repository.list() == []

    def test_leaves_the_other_tasks(self, repository):
        first = repository.add("Buy groceries", NOW)
        repository.add("Cook dinner", NOW)

        repository.delete(first.id)

        [task] = repository.list()
        assert task.description == "Cook dinner"

    def test_raises_not_found_for_an_unknown_id(self, repository):
        with pytest.raises(TaskNotFoundError):
            repository.delete(99)


class TestList:
    def test_orders_by_id(self, repository):
        repository.add("Buy groceries", NOW)
        repository.add("Cook dinner", NOW)

        assert [task.id for task in repository.list()] == [1, 2]

    def test_filters_by_status(self, repository):
        repository.add("Buy groceries", NOW)
        done = repository.add("Cook dinner", NOW)
        repository.update(
            done.id, description=None, status=Status.DONE, updated_at=LATER
        )

        [task] = repository.list(Status.DONE)
        assert task.description == "Cook dinner"
