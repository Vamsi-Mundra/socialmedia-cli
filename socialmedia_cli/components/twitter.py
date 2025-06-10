"""
Twitter-specific API wrapper.
"""

import json
from pathlib import Path
from typing import Tuple
from requests_oauthlib import OAuth1Session

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
        # Initialize OAuth1Session with stored credentials
        oauth = OAuth1Session(
            t["consumer_key"],
            client_secret=t["consumer_secret"],
            resource_owner_key=t["access_token"],
            resource_owner_secret=t["access_token_secret"]
        )

        # Prepare the tweet payload
        payload = {"text": text}

        # Make the request to Twitter API v2
        response = oauth.post(
            "https://api.twitter.com/2/tweets",
            json=payload
        )

        if response.status_code != 201:
            raise ValueError(f"Request returned an error: {response.status_code} {response.text}")

        # Parse the response
        json_response = response.json()
        if not json_response or 'data' not in json_response:
            raise ValueError("Invalid response from Twitter API")

        tweet_id = json_response['data']['id']
        tweet_url = f"https://twitter.com/user/status/{tweet_id}"
        
        # Print success message
        print(f"Successfully posted tweet!")
        print(f"Tweet URL: {tweet_url}")
        
        return tweet_id, tweet_url

    except Exception as e:
        print(f"Error posting tweet: {str(e)}")
        raise ValueError(f"Failed to post tweet: {str(e)}") 