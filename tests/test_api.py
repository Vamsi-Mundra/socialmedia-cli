"""
Tests for the API dispatcher.
"""

import pytest
from unittest import mock
from socialmedia_cli import api
from socialmedia_cli.components import twitter


def test_post_twitter(tmp_path, monkeypatch):
    """Test that posting to Twitter routes to twitter.post_tweet."""
    # Mock twitter.post_tweet
    mock_result = ("12345", "https://twitter.com/user/status/12345")
    monkeypatch.setattr(twitter, "post_tweet", mock.Mock(return_value=mock_result))
    # Call api.post
    result = api.post("twitter", "Hello!")
    # Verify routing
    assert result == mock_result
    twitter.post_tweet.assert_called_with("Hello!")


def test_post_unsupported_platform():
    """Test that posting to an unsupported platform raises ValueError."""
    with pytest.raises(ValueError, match="Unsupported platform"):
        api.post("facebook", "Hello!") 