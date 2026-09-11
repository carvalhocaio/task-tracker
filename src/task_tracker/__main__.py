"""Composition root: opens the JSON repository, wires the task service,
and hands control to the CLI session. Everything the layers below need is
chosen here and nowhere else.
"""

import sys

from task_tracker.application.task_service import TaskService
from task_tracker.infrastructure.cli.session import Session
from task_tracker.infrastructure.json_repository import JsonRepository

DATA_PATH = "tasks.json"


def main() -> None:
    repository = JsonRepository(DATA_PATH)
    service = TaskService(repository)
    session = Session(service)
    sys.exit(session.run(sys.argv[1:]))


if __name__ == "__main__":
    main()
