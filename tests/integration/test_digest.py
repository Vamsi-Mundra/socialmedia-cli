"""Integration tests for daily digest pipeline."""
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from socialmedia_cli.pipelines.daily_digest import run
from socialmedia_cli.writers.tweet_writer import DraftTweet

@pytest.fixture
def mock_collect():
    """Mock web search collector."""
    with patch("socialmedia_cli.collectors.web_search.collect") as mock:
        mock.return_value = [
            "Test bullet point 1",
            "Test bullet point 2",
            "Test bullet point 3"
        ]
        yield mock

@pytest.fixture
def mock_draft():
    """Mock tweet drafting."""
    with patch("socialmedia_cli.writers.tweet_writer.draft") as mock:
        mock.return_value = [
            DraftTweet(id="1", text="Test tweet 1"),
            DraftTweet(id="2", text="Test tweet 2"),
            DraftTweet(id="3", text="Test tweet 3")
        ]
        yield mock

@pytest.fixture
def mock_refine():
    """Mock tweet refinement."""
    with patch("socialmedia_cli.writers.tweet_writer.refine") as mock:
        mock.return_value = [
            DraftTweet(id="1", text="Test tweet 1", score=0.8, reason="Good"),
            DraftTweet(id="2", text="Test tweet 2", score=0.6, reason="OK"),
            DraftTweet(id="3", text="Test tweet 3", score=0.4, reason="Poor")
        ]
        yield mock

def test_digest_pipeline(tmp_path, mock_collect, mock_draft, mock_refine):
    """Test the complete digest pipeline."""
    # Run pipeline
    path = run(
        topic="test",
        hours=24,
        tweets=3,
        chars=280,
        provider="fake",
        model="test-model",
        out_dir=tmp_path
    )
    
    # Verify output file
    assert path.exists()
    records = []
    with open(path) as f:
        for line in f:
            records.append(json.loads(line))
    
    # Verify content
    assert len(records) == 3
    assert all("id" in r for r in records)
    assert all("text" in r for r in records)
    assert all("score" in r for r in records)
    assert all("reason" in r for r in records)
    
    # Verify sorting by score
    scores = [r["score"] for r in records]
    assert scores == sorted(scores, reverse=True) 