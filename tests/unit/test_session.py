"""Tests for the CLI Session dispatch loop, wired against
TaskService(fake_repository) with captured Rich consoles instead of real
stdout/stderr."""

import io

import pytest
from rich.console import Console

from task_tracker.application.task_service import TaskService
from task_tracker.infrastructure.cli.session import Session


class CapturedSession:
    """A Session wired to in-memory consoles, exposing what each one saw."""

    def __init__(self, service):
        self._console = Console(file=io.StringIO(), width=200)
        self._error_console = Console(file=io.StringIO(), width=200)
        self._session = Session(
            service, console=self._console, error_console=self._error_console
        )

    def run(self, argv):
        return self._session.run(argv)

    @property
    def out(self):
        return self._console.file.getvalue()

    @property
    def err(self):
        return self._error_console.file.getvalue()

    def run_capturing(self, argv):
        """Runs a command and returns only the output it produced, so an
        assertion can't accidentally match an earlier command's output."""
        before = len(self.out)
        self.run(argv)
        return self.out[before:]


@pytest.fixture
def session(fake_repository, fixed_clock):
    return CapturedSession(TaskService(fake_repository, clock=fixed_clock))


class TestAdd:
    def test_prints_success_with_the_new_id(self, session):
        code = session.run(["add", "Buy groceries"])

        assert code == 0
        assert "Task added successfully (ID: 1)" in session.out

    def test_blank_description_is_an_error(self, session):
        code = session.run(["add", "   "])

        assert code == 1
        assert "description cannot be empty" in session.err


class TestUpdate:
    def test_prints_success(self, session):
        session.run(["add", "Buy groceries"])

        code = session.run(["update", "1", "Buy groceries and cook dinner"])

        assert code == 0
        assert "Task 1 updated successfully" in session.out

    def test_unknown_id_is_an_error(self, session):
        code = session.run(["update", "99", "Nothing here"])

        assert code == 1
        assert "task with id 99 not found" in session.err


class TestDelete:
    def test_prints_success(self, session):
        session.run(["add", "Buy groceries"])

        code = session.run(["delete", "1"])

        assert code == 0
        assert "Task 1 deleted successfully" in session.out

    def test_unknown_id_is_an_error(self, session):
        code = session.run(["delete", "99"])

        assert code == 1
        assert "task with id 99 not found" in session.err


class TestMark:
    @pytest.mark.parametrize(
        ("command", "label"),
        [("mark-in-progress", "in-progress"), ("mark-done", "done")],
    )
    def test_prints_the_new_status(self, session, command, label):
        session.run(["add", "Buy groceries"])

        code = session.run([command, "1"])

        assert code == 0
        assert f"Task 1 marked as {label}" in session.out

    def test_unknown_id_is_an_error(self, session):
        code = session.run(["mark-done", "99"])

        assert code == 1
        assert "task with id 99 not found" in session.err


class TestList:
    def test_prints_a_table_of_tasks(self, session):
        session.run(["add", "Buy groceries"])

        code = session.run(["list"])

        assert code == 0
        assert "Buy groceries" in session.out

    def test_prints_a_placeholder_when_empty(self, session):
        session.run(["list"])

        assert "No tasks found." in session.out

    def test_filters_by_status(self, session):
        session.run(["add", "Buy groceries"])
        session.run(["add", "Cook dinner"])
        session.run(["mark-done", "2"])

        rendered = session.run_capturing(["list", "done"])

        assert "Cook dinner" in rendered
        assert "Buy groceries" not in rendered


class TestExitCodes:
    def test_successful_command_returns_zero(self, session):
        assert session.run(["list"]) == 0

    def test_app_error_returns_one_and_writes_to_stderr(self, session):
        assert session.run(["delete", "99"]) == 1
        assert "Error:" in session.err
        assert session.err != ""
