"""
Tests for the CLI interface.
"""

import subprocess
from pathlib import Path
import pytest
from unittest import mock
from socialmedia_cli import cli


def test_cli_help():
    """Test that --help shows available commands."""
    result = subprocess.run(
        ["socialmedia-cli", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "login" in result.stdout
    assert "post" in result.stdout


def test_invalid_command():
    """Test that invalid commands exit with code 1 and print a usage hint."""
    result = subprocess.run(
        ["socialmedia-cli", "invalid"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 1
    assert "usage:" in result.stderr
    assert "invalid choice" in result.stderr or "error:" in result.stderr


def test_login_command(monkeypatch, capsys):
    """Test the login command via cli.main()."""
    # Mock auth.login to do nothing
    monkeypatch.setattr(cli.auth, "login", mock.Mock())
    exit_code = cli.main(["login", "twitter"])
    out, err = capsys.readouterr()
    assert exit_code == 0
    cli.auth.login.assert_called_with("twitter")


def test_post_command(monkeypatch, capsys):
    """Test the post command via cli.main()."""
    # Mock api.post to return a dummy result
    monkeypatch.setattr(cli.api, "post", mock.Mock(return_value=("12345", "https://twitter.com/user/status/12345")))
    exit_code = cli.main(["post", "twitter", "Hello!"])
    out, err = capsys.readouterr()
    assert exit_code == 0
    cli.api.post.assert_called_with("twitter", "Hello!") 