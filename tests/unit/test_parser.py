"""Tests for the argparse CLI surface, which keeps the positional style
the roadmap.sh brief documents."""

import pytest

from task_tracker.infrastructure.cli.parser import build_parser


@pytest.fixture
def parser():
    return build_parser()


class TestAdd:
    def test_parses_the_description(self, parser):
        args = parser.parse_args(["add", "Buy groceries"])

        assert args.command == "add"
        assert args.description == "Buy groceries"

    def test_requires_a_description(self, parser):
        with pytest.raises(SystemExit):
            parser.parse_args(["add"])


class TestUpdate:
    def test_parses_id_and_description(self, parser):
        args = parser.parse_args(["update", "1", "Buy groceries and cook dinner"])

        assert args.id == 1
        assert args.description == "Buy groceries and cook dinner"

    def test_rejects_a_non_numeric_id(self, parser):
        with pytest.raises(SystemExit):
            parser.parse_args(["update", "abc", "x"])

    def test_requires_a_description(self, parser):
        with pytest.raises(SystemExit):
            parser.parse_args(["update", "1"])


class TestDelete:
    def test_parses_the_id(self, parser):
        args = parser.parse_args(["delete", "1"])

        assert args.command == "delete"
        assert args.id == 1


class TestMark:
    @pytest.mark.parametrize("command", ["mark-in-progress", "mark-done"])
    def test_parses_the_id(self, parser, command):
        args = parser.parse_args([command, "1"])

        assert args.command == command
        assert args.id == 1

    def test_has_no_mark_todo_command(self, parser):
        """The roadmap.sh brief only defines the two forward transitions."""
        with pytest.raises(SystemExit):
            parser.parse_args(["mark-todo", "1"])


class TestList:
    def test_defaults_the_filter_to_none(self, parser):
        args = parser.parse_args(["list"])

        assert args.command == "list"
        assert args.status is None

    @pytest.mark.parametrize("status", ["todo", "in-progress", "done"])
    def test_accepts_each_known_status(self, parser, status):
        assert parser.parse_args(["list", status]).status == status

    def test_rejects_an_unknown_filter(self, parser):
        with pytest.raises(SystemExit):
            parser.parse_args(["list", "bogus"])


class TestUnknownCommand:
    def test_raises_system_exit(self, parser):
        with pytest.raises(SystemExit):
            parser.parse_args(["frobnicate"])

    def test_no_command_raises_system_exit(self, parser):
        with pytest.raises(SystemExit):
            parser.parse_args([])
