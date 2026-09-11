"""Tests for the pure domain model."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from task_tracker.domain.task import Status, Task
from task_tracker.errors import InvalidStatusError

NOW = datetime(2026, 9, 11, 12, 0, tzinfo=UTC)


class TestStatus:
    @pytest.mark.parametrize(
        ("member", "value"),
        [
            (Status.TODO, "todo"),
            (Status.IN_PROGRESS, "in-progress"),
            (Status.DONE, "done"),
        ],
    )
    def test_wire_value_matches_the_cli_vocabulary(self, member, value):
        assert member.value == value
        assert str(member) == value

    def test_parses_a_known_value(self):
        assert Status.parse("in-progress") is Status.IN_PROGRESS

    def test_rejects_an_unknown_value(self):
        with pytest.raises(InvalidStatusError):
            Status.parse("bogus")

    def test_values_lists_every_member_in_lifecycle_order(self):
        assert Status.values() == ("todo", "in-progress", "done")


class TestTask:
    def test_is_immutable(self):
        task = Task(
            id=1,
            description="Buy groceries",
            status=Status.TODO,
            created_at=NOW,
            updated_at=NOW,
        )

        with pytest.raises(FrozenInstanceError):
            task.description = "Something else"
