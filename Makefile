.PHONY: help sync run test lint lint-fix format format-check check

help:
	@echo "Available commands in Makefile:"
	@echo "  make help         - Show this help message"
	@echo "  make sync         - Install runtime + dev dependencies"
	@echo "  make run          - Run the CLI (uv run task-cli)"
	@echo "  make test         - Run tests (pytest -v)"
	@echo "  make lint         - Run linter (ruff check)"
	@echo "  make lint-fix     - Automatically fix linter issues (ruff check --fix)"
	@echo "  make format       - Format code (ruff format)"
	@echo "  make format-check - Check code formatting (ruff format --check)"
	@echo "  make check        - Run linter, format check, and tests"

sync:
	uv sync

run:
	uv run task-cli

test:
	uv run pytest -v

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check --fix .

format:
	uv run ruff format .

format-check:
	uv run ruff format --check .

check: lint format-check test
