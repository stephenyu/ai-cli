"""Tests for top-level argument handling in main.py."""

from ai_cli.main import handle_implicit_query


def test_bare_question_gets_query_inserted():
    assert handle_implicit_query(["ai", "list python files"]) == [
        "ai", "query", "list python files"
    ]


def test_known_subcommand_passes_through():
    assert handle_implicit_query(["ai", "status"]) == ["ai", "status"]


def test_help_flag_is_not_rewritten_as_a_query():
    assert handle_implicit_query(["ai", "--help"]) == ["ai", "--help"]
    assert handle_implicit_query(["ai", "-h"]) == ["ai", "-h"]


def test_version_flag_is_not_rewritten_as_a_query():
    assert handle_implicit_query(["ai", "--version"]) == ["ai", "--version"]


def test_program_name_only_is_unchanged():
    assert handle_implicit_query(["ai"]) == ["ai"]
