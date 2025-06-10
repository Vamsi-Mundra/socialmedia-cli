"""
Tests for the Twitter component.
"""

import json
import pytest
from unittest import mock
from socialmedia_cli.components import twitter

def test_post_tweet_no_token_file(tmp_path, monkeypatch):
    """Test that posting a tweet without a token file raises FileNotFoundError."""
    # Patch TOKEN_PATH to a temp location that does not exist
    monkeypatch.setattr(twitter, "TOKEN_PATH", tmp_path / "no_token.json")
    with pytest.raises(FileNotFoundError):
        twitter.post_tweet("Test tweet")

def test_post_tweet_success(tmp_path, monkeypatch):
    """Test posting a tweet with valid tokens returns (id, url)."""
    # Write valid tokens
    token_path = tmp_path / "tokens.json"
    tokens = {
        "twitter": {
            "access_token": "atoken",
            "access_token_secret": "asecret",
            "consumer_key": "ckey",
            "consumer_secret": "csecret"
        }
    }
    token_path.write_text(json.dumps(tokens))
    monkeypatch.setattr(twitter, "TOKEN_PATH", token_path)
    # Mock tweepy
    mock_status = mock.Mock()
    mock_status.id = 12345
    mock_api = mock.Mock()
    mock_api.update_status.return_value = mock_status
    monkeypatch.setattr(twitter.tweepy, "OAuth1UserHandler", mock.Mock())
    monkeypatch.setattr(twitter.tweepy, "API", mock.Mock(return_value=mock_api))
    tweet_id, tweet_url = twitter.post_tweet("Hello!")
    assert tweet_id == "12345"
    assert tweet_url == "https://twitter.com/user/status/12345"
    mock_api.update_status.assert_called_with("Hello!")

def test_post_tweet_invalid_tokens(tmp_path, monkeypatch):
    """Test that invalid tokens raise ValueError."""
    # Write incomplete tokens
    token_path = tmp_path / "tokens.json"
    tokens = {"twitter": {"access_token": "atoken"}}  # missing keys
    token_path.write_text(json.dumps(tokens))
    monkeypatch.setattr(twitter, "TOKEN_PATH", token_path)
    with pytest.raises(ValueError, match="missing required keys"):
        twitter.post_tweet("Hello!")

def test_post_tweet_tweepy_error(tmp_path, monkeypatch):
    """Test that Tweepy errors are raised as ValueError."""
    # Write valid tokens
    token_path = tmp_path / "tokens.json"
    tokens = {
        "twitter": {
            "access_token": "atoken",
            "access_token_secret": "asecret",
            "consumer_key": "ckey",
            "consumer_secret": "csecret"
        }
    }
    token_path.write_text(json.dumps(tokens))
    monkeypatch.setattr(twitter, "TOKEN_PATH", token_path)
    # Mock tweepy to raise
    monkeypatch.setattr(twitter.tweepy, "OAuth1UserHandler", mock.Mock())
    mock_api = mock.Mock()
    mock_api.update_status.side_effect = twitter.tweepy.TweepyException("fail")
    monkeypatch.setattr(twitter.tweepy, "API", mock.Mock(return_value=mock_api))
    with pytest.raises(ValueError, match="Failed to post tweet"):
        twitter.post_tweet("fail!") 