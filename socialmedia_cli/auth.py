"""
Authentication module for social media platforms.
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, Tuple
import tweepy
from urllib.parse import parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import webbrowser
from .components import twitter

TOKEN_PATH = Path.home() / ".socialmedia_cli_tokens.json"
TOKEN_MODE = 0o600
CALLBACK_PORT = 8000
CALLBACK_URL = f"http://localhost:{CALLBACK_PORT}/callback"

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback and store the verifier."""
    verifier = None
    
    def do_GET(self):
        """Handle GET request to callback URL."""
        if self.path.startswith('/callback'):
            # Parse the callback URL
            query = parse_qs(urlparse(self.path).query)
            OAuthCallbackHandler.verifier = query.get('oauth_verifier', [None])[0]
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # HTML response
            html = """
                <html>
                    <body style="text-align: center; font-family: Arial, sans-serif; margin-top: 50px;">
                        <h1 style="color: #1DA1F2;">Authentication Successful!</h1>
                        <p>You can close this window and return to the terminal.</p>
                    </body>
                </html>
            """
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_error(404)

def get_twitter_credentials() -> tuple[str, str]:
    """Get Twitter API credentials, prompting user if not set."""
    consumer_key = os.environ.get("TWITTER_CONSUMER_KEY")
    consumer_secret = os.environ.get("TWITTER_CONSUMER_SECRET")
    
    if not consumer_key or not consumer_secret:
        print("\nTo use Twitter, you need to set up API credentials:")
        print("1. Go to https://developer.twitter.com/en/portal/dashboard")
        print("2. Create a new app or use an existing one")
        print("3. Get your API Key (Consumer Key) and API Secret (Consumer Secret)")
        print("4. In User authentication settings:")
        print(f"   - Enable OAuth 1.0a")
        print(f"   - Set callback URL to: {CALLBACK_URL}")
        print("\nThen set them as environment variables:")
        print("export TWITTER_CONSUMER_KEY='your_consumer_key'")
        print("export TWITTER_CONSUMER_SECRET='your_consumer_secret'")
        print("\nOr enter them now (they will be used only for this session):")
        consumer_key = input("Enter your Twitter API Key (Consumer Key): ").strip()
        consumer_secret = input("Enter your Twitter API Secret (Consumer Secret): ").strip()
    
    return consumer_key, consumer_secret

def start_callback_server() -> HTTPServer:
    """Start a local server to handle the OAuth callback."""
    server = HTTPServer(('localhost', CALLBACK_PORT), OAuthCallbackHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    return server

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
    
    try:
        # Get Twitter API credentials
        consumer_key, consumer_secret = get_twitter_credentials()
        
        # Initialize OAuth handler
        auth = tweepy.OAuth1UserHandler(
            consumer_key, 
            consumer_secret,
            callback=CALLBACK_URL
        )
        
        try:
            # Start callback server
            print("\nStarting local server to handle authentication...")
            server = start_callback_server()
            
            # Get request token and authorization URL
            redirect_url = auth.get_authorization_url()
            print(f"\nOpening browser for Twitter authorization...")
            webbrowser.open(redirect_url)
            
            print("\nWaiting for Twitter callback...")
            # Wait for callback with timeout
            timeout = 120  # 2 minutes
            start_time = time.time()
            while not OAuthCallbackHandler.verifier:
                if time.time() - start_time > timeout:
                    server.shutdown()
                    raise Exception("Authentication timed out. Please try again.")
                time.sleep(1)
            
            # Shutdown server
            server.shutdown()
            
            # Exchange for access token
            auth.get_access_token(OAuthCallbackHandler.verifier)
            
            # Save tokens
            tokens = {
                "twitter": {
                    "access_token": auth.access_token,
                    "access_token_secret": auth.access_token_secret,
                    "consumer_key": consumer_key,
                    "consumer_secret": consumer_secret
                }
            }
            
            with open(TOKEN_PATH, "w") as f:
                json.dump(tokens, f, indent=2)
            os.chmod(TOKEN_PATH, TOKEN_MODE)
            
            print(f"\n✅ Authentication successful!")
            print(f"Tokens saved to {TOKEN_PATH}")
            
            # Wait and run smoke test
            # print("\nWaiting 60 seconds before running a test post...")
            # time.sleep(60)
            # print("Posting test tweet...")
            
            # try:
            #     tweet_id, tweet_url = twitter.post_tweet("Hello to my workld!!")
            #     print(f"✅ Test successful! Tweet posted: {tweet_url}")
            # except Exception as e:
            #     print(f"⚠️  Test post failed: {e}")
            #     print("You can still try posting manually with: socialmedia-cli post twitter 'your message'")
                
        except tweepy.TweepyException as e:
            raise Exception(f"Failed to complete authentication: {e}")
            
    except Exception as e:
        raise Exception(f"Twitter login failed: {e}") 