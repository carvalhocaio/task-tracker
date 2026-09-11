"""Tests for TaskService, exercised against FakeTaskRepository so no test
here touches the filesystem."""

import pytest

from task_tracker.application.task_service import TaskService
from task_tracker.domain.task import Status
from task_tracker.errors import EmptyDescriptionError, TaskNotFoundError


@pytest.fixture
def service(fake_repository, fixed_clock):
    return TaskService(fake_repository, clock=fixed_clock)


class TestAdd:
    def test_returns_the_new_task(self, service):
        task = service.add("Buy groceries")

        assert task.id == 1
        assert task.description == "Buy groceries"

    def test_starts_in_todo(self, service):
        assert service.add("Buy groceries").status is Status.TODO

    def test_stamps_both_timestamps_with_the_same_instant(self, service):
        task = service.add("Buy groceries")

        assert task.created_at == task.updated_at

    def test_strips_surrounding_whitespace(self, service):
        assert service.add("  Buy groceries  ").description == "Buy groceries"

    @pytest.mark.parametrize("description", ["", "   ", "\t\n"])
    def test_rejects_a_blank_description(self, service, description):
        with pytest.raises(EmptyDescriptionError):
            service.add(description)


class TestUpdate:
    def test_changes_the_description(self, service):
        task = service.add("Buy groceries")

        updated = service.update(task.id, "Buy groceries and cook dinner")

        assert updated.description == "Buy groceries and cook dinner"

    def test_refreshes_updated_at_but_not_created_at(self, service):
        task = service.add("Buy groceries")

        updated = service.update(task.id, "Buy groceries and cook dinner")

        assert updated.updated_at > task.updated_at
        assert updated.created_at == task.created_at

    def test_leaves_the_status_alone(self, service):
        task = service.add("Buy groceries")
        service.set_status(task.id, Status.DONE)

        assert service.update(task.id, "Still done").status is Status.DONE

    @pytest.mark.parametrize("description", ["", "   "])
    def test_rejects_a_blank_description(self, service, description):
        task = service.add("Buy groceries")

        with pytest.raises(EmptyDescriptionError):
            service.update(task.id, description)

    def test_propagates_not_found(self, service):
        with pytest.raises(TaskNotFoundError):
            service.update(99, "Nothing here")


class TestDelete:
    def test_deletes_an_existing_task(self, service):
        task = service.add("Buy groceries")

        service.delete(task.id)

        assert service.list() == []

    def test_propagates_not_found(self, service):
        with pytest.raises(TaskNotFoundError):
            service.delete(99)


class TestSetStatus:
    @pytest.mark.parametrize("status", list(Status))
    def test_sets_each_status(self, service, status):
        task = service.add("Buy groceries")

        assert service.set_status(task.id, status).status is status

    def test_refreshes_updated_at(self, service):
        task = service.add("Buy groceries")

        updated = service.set_status(task.id, Status.DONE)

        assert updated.updated_at > task.updated_at

    def test_propagates_not_found(self, service):
        with pytest.raises(TaskNotFoundError):
            service.set_status(99, Status.DONE)


class TestList:
    def test_lists_everything_with_no_filter(self, service):
        service.add("Buy groceries")
        service.add("Cook dinner")

        assert len(service.list()) == 2

    def test_filters_by_status(self, service):
        service.add("Buy groceries")
        done = service.add("Cook dinner")
        service.set_status(done.id, Status.DONE)

        [task] = service.list(Status.DONE)
        assert task.description == "Cook dinner"

    def test_returns_empty_when_nothing_matches(self, service):
        service.add("Buy groceries")

        assert service.list(Status.DONE) == []
