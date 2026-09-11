"""Pure task model and status vocabulary -- no I/O, no persistence."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from task_tracker.errors import InvalidStatusError


class Status(StrEnum):
    """Lifecycle state of a Task. Members are declared in lifecycle order,
    which is the order `values()` reports and the CLI offers.
    """

    TODO = "todo"
    IN_PROGRESS = "in-progress"
    DONE = "done"

    @classmethod
    def parse(cls, value: str) -> "Status":
        """Resolves a wire value, raising InvalidStatusError instead of the
        bare ValueError StrEnum would give -- this is what replaces the Go
        version's hand-rolled IsValid() switch.
        """
        try:
            return cls(value)
        except ValueError as error:
            raise InvalidStatusError(value) from error

    @classmethod
    def values(cls) -> tuple[str, ...]:
        return tuple(status.value for status in cls)


@dataclass(frozen=True, slots=True)
class Task:
    id: int
    description: str
    status: Status
    created_at: datetime
    updated_at: datetime
