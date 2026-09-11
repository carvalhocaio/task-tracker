"""Tests for the Rich presentation layer, driven through a Console
writing to a StringIO instead of a real terminal."""

import io
from datetime import UTC, datetime

import pytest
from rich.console import Console

from task_tracker.domain.task import Status, Task
from task_tracker.infrastructure.cli import output

NOW = datetime(2026, 9, 11, 12, 0, tzinfo=UTC)


def make_task(task_id=1, description="Buy groceries", status=Status.TODO):
    return Task(
        id=task_id,
        description=description,
        status=status,
        created_at=NOW,
        updated_at=NOW,
    )


@pytest.fixture
def console():
    return Console(file=io.StringIO(), width=200)


def text_of(console):
    return console.file.getvalue()


class TestPrintTaskAdded:
    def test_reports_the_new_id(self, console):
        output.print_task_added(console, make_task())

        assert "Task added successfully (ID: 1)" in text_of(console)


class TestPrintTasks:
    def test_shows_a_placeholder_when_empty(self, console):
        output.print_tasks(console, [])

        assert "No tasks found." in text_of(console)

    def test_lists_every_description(self, console):
        output.print_tasks(
            console, [make_task(1, "Buy groceries"), make_task(2, "Cook dinner")]
        )

        assert "Buy groceries" in text_of(console)
        assert "Cook dinner" in text_of(console)

    def test_shows_the_column_headers(self, console):
        output.print_tasks(console, [make_task()])

        rendered = text_of(console)
        for header in ("ID", "Status", "Description", "Created", "Updated"):
            assert header in rendered

    @pytest.mark.parametrize("status", list(Status))
    def test_shows_each_status_label(self, console, status):
        output.print_tasks(console, [make_task(status=status)])

        assert status.value in text_of(console)

    def test_formats_timestamps_to_the_minute(self, console):
        output.print_tasks(console, [make_task()])

        assert "2026-09-11 12:00" in text_of(console)


class TestStatusStyles:
    def test_every_status_has_a_style(self):
        assert set(output.STATUS_STYLES) == set(Status)
