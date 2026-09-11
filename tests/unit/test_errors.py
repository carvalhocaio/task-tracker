"""Tests for the centralized AppError hierarchy."""

import pytest

from task_tracker.errors import (
    AppError,
    CorruptDataError,
    EmptyDescriptionError,
    InvalidStatusError,
    StorageError,
    TaskNotFoundError,
)


class TestTaskNotFoundError:
    def test_message_includes_the_task_id(self):
        error = TaskNotFoundError(5)

        assert str(error) == "task with id 5 not found"
        assert error.task_id == 5
        assert isinstance(error, AppError)


class TestEmptyDescriptionError:
    def test_has_expected_message(self):
        error = EmptyDescriptionError()

        assert str(error) == "description cannot be empty"
        assert isinstance(error, AppError)


class TestInvalidStatusError:
    def test_message_lists_the_known_statuses(self):
        error = InvalidStatusError("bogus")

        assert str(error) == "invalid status 'bogus' (use: todo, in-progress, done)"
        assert error.value == "bogus"
        assert isinstance(error, AppError)


class TestWrappedCauseErrors:
    @pytest.mark.parametrize(
        ("error_type", "prefix"),
        [
            (StorageError, "storage error:"),
            (CorruptDataError, "corrupt data:"),
        ],
    )
    def test_message_includes_the_wrapped_cause(self, error_type, prefix):
        cause = ValueError("boom")

        error = error_type(cause)

        assert str(error) == f"{prefix} {cause}"
        assert error.cause is cause
        assert isinstance(error, AppError)
