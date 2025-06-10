"""
Twitter-specific API wrapper.
"""

import json
from pathlib import Path
from typing import Tuple
import tweepy

TOKEN_PATH = Path.home() / ".socialmedia_cli_tokens.json"


def post_tweet(text: str) -> Tuple[str, str]:
    """
    Post a tweet using stored OAuth credentials.
    
    Args:
        text: The tweet text to post
        
    Returns:
        Tuple of (tweet_id, tweet_url)
        
    Raises:
        FileNotFoundError: If token file is missing
        ValueError: If tokens are invalid or revoked
    """
    if not TOKEN_PATH.exists():
        raise FileNotFoundError(f"Token file not found: {TOKEN_PATH}")
    with open(TOKEN_PATH) as f:
        tokens = json.load(f)
    if "twitter" not in tokens:
        raise ValueError("No Twitter tokens found in token file.")
    t = tokens["twitter"]
    required_keys = ["access_token", "access_token_secret", "consumer_key", "consumer_secret"]
    if not all(k in t for k in required_keys):
        raise ValueError("Twitter token file is missing required keys.")
    try:
        auth = tweepy.OAuth1UserHandler(
            t["consumer_key"],
            t["consumer_secret"],
            t["access_token"],
            t["access_token_secret"]
        )
        api = tweepy.API(auth)
        status = api.update_status(text)
        tweet_id = str(status.id)
        tweet_url = f"https://twitter.com/user/status/{tweet_id}"
        return tweet_id, tweet_url
    except tweepy.TweepyException as e:
        raise ValueError(f"Failed to post tweet: {e}") 