"""
Authentication module for social media platforms.
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, Tuple
import tweepy
from .components import twitter

TOKEN_PATH = Path.home() / ".socialmedia_cli_tokens.json"
TOKEN_MODE = 0o600

def login(platform: str) -> None:
    """
    Authenticate with the specified social media platform.
    
    Args:
        platform: The platform to authenticate with (e.g., 'twitter')
        
    Raises:
        ValueError: If the platform is not supported
        Exception: For network or authentication errors
    """
    if platform != "twitter":
        raise ValueError(f"Unsupported platform: {platform}")
    # Read keys at call time for testability
    CONSUMER_KEY = os.environ.get("TWITTER_CONSUMER_KEY", "YOUR_CONSUMER_KEY")
    CONSUMER_SECRET = os.environ.get("TWITTER_CONSUMER_SECRET", "YOUR_CONSUMER_SECRET")
    try:
        auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET)
        try:
            redirect_url = auth.get_authorization_url()
        except tweepy.TweepyException as e:
            raise Exception(f"Failed to get request token: {e}")
        print(f"Go to the following URL to authorize:\n{redirect_url}")
        verifier = input("Enter the PIN (oauth_verifier) from Twitter: ").strip()
        try:
            auth.get_access_token(verifier)
        except tweepy.TweepyException as e:
            raise Exception(f"Failed to get access token: {e}")
        tokens = {
            "twitter": {
                "access_token": auth.access_token,
                "access_token_secret": auth.access_token_secret,
                "consumer_key": CONSUMER_KEY,
                "consumer_secret": CONSUMER_SECRET
            }
        }
        with open(TOKEN_PATH, "w") as f:
            json.dump(tokens, f, indent=2)
        os.chmod(TOKEN_PATH, TOKEN_MODE)
        print(f"Tokens saved to {TOKEN_PATH} (mode 0o600)")
        print("Waiting 60 seconds before smoke test...")
        time.sleep(60)
        print("Running smoke test: posting a hello tweet...")
        try:
            tweet_id, tweet_url = twitter.post_tweet("Hello to my workld!!")
            print(f"Smoke test successful: {tweet_url}")
        except Exception as e:
            print(f"Smoke test failed: {e}")
    except Exception as e:
        raise Exception(f"Twitter login failed: {e}") 