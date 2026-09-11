"""Centralized application error hierarchy. Every layer (infrastructure,
application, cli) raises or wraps into one of these, so the CLI's
composition root has exactly one type to catch and one place to decide
exit codes -- replacing the sentinel errors the Go version scattered
across its app package.
"""


class AppError(Exception):
    """Base for every error the application can raise."""


class TaskNotFoundError(AppError):
    def __init__(self, task_id: int) -> None:
        super().__init__(f"task with id {task_id} not found")
        self.task_id = task_id


class EmptyDescriptionError(AppError):
    def __init__(self) -> None:
        super().__init__("description cannot be empty")


class InvalidStatusError(AppError):
    """Raised when a string can't be resolved to a Status. The CLI parser
    normally rejects bad filters first; this guards the service for any
    other caller."""

    def __init__(self, value: str) -> None:
        super().__init__(f"invalid status '{value}' (use: todo, in-progress, done)")
        self.value = value


class StorageError(AppError):
    """Wraps an OSError from reading or writing the task file."""

    def __init__(self, cause: Exception) -> None:
        super().__init__(f"storage error: {cause}")
        self.cause = cause


class CorruptDataError(AppError):
    """Raised when the task file exists but isn't the JSON shape we wrote
    -- invalid JSON, not a list, or a record with a missing/unparseable
    field. The Go version only caught the first of those."""

    def __init__(self, cause: Exception) -> None:
        super().__init__(f"corrupt data: {cause}")
        self.cause = cause
