"""
Tests for the authentication module.
"""

import json
from pathlib import Path
import pytest
import builtins
from unittest import mock
from socialmedia_cli import auth

def test_unsupported_platform():
    """Test that unsupported platforms raise ValueError."""
    with pytest.raises(ValueError, match="Unsupported platform"):
        auth.login("facebook")

@pytest.mark.skip(reason="Twitter login flow requires manual OAuth interaction")
def test_twitter_login_flow(tmp_path, monkeypatch):
    """Test the full Twitter login flow, including token file and smoke test."""
    # Patch environment for consumer keys
    monkeypatch.setenv("TWITTER_CONSUMER_KEY", "ckey")
    monkeypatch.setenv("TWITTER_CONSUMER_SECRET", "csecret")
    # Patch token path to temp
    token_path = tmp_path / ".socialmedia_cli_tokens.json"
    monkeypatch.setattr(auth, "TOKEN_PATH", token_path)
    # Patch Tweepy OAuth handler
    mock_handler = mock.Mock()
    mock_handler.get_authorization_url.return_value = "http://auth.url"
    mock_handler.get_access_token.return_value = None
    mock_handler.access_token = "atoken"
    mock_handler.access_token_secret = "asecret"
    monkeypatch.setattr(auth.tweepy, "OAuth1UserHandler", mock.Mock(return_value=mock_handler))
    # Patch input to simulate user entering verifier
    monkeypatch.setattr(builtins, "input", lambda _: "verifier123")
    # Patch os.chmod to do nothing
    monkeypatch.setattr(auth.os, "chmod", lambda *a, **kw: None)
    # Patch time.sleep to avoid real delay
    monkeypatch.setattr(auth.time, "sleep", lambda s: None)
    # Patch smoke test post_tweet
    smoke_result = ("12345", "https://twitter.com/user/status/12345")
    monkeypatch.setattr(auth.twitter, "post_tweet", mock.Mock(return_value=smoke_result))
    # Run login
    auth.login("twitter")
    # Check token file written
    with open(token_path) as f:
        tokens = json.load(f)
    assert "twitter" in tokens
    t = tokens["twitter"]
    assert t["access_token"] == "atoken"
    assert t["access_token_secret"] == "asecret"
    assert t["consumer_key"] == "ckey"
    assert t["consumer_secret"] == "csecret"
    # Check smoke test was called
    auth.twitter.post_tweet.assert_called_with("Hello to my workld!!") 