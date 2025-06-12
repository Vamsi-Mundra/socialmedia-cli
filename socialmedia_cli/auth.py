"""
Authentication module for social media platforms.
"""

import json
import os
import time
import socket
from pathlib import Path
from typing import Dict, Tuple
import tweepy
from urllib.parse import parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import webbrowser
from .components import twitter
from .core.config import get_config_value
from .core.logging import get_logger

logger = get_logger("auth")

# Get configuration values
TOKEN_PATH = Path(get_config_value('auth.token_path'))
TOKEN_MODE = int(get_config_value('auth.token_mode'), 8)  # Convert string to octal
CALLBACK_PORT = get_config_value('auth.callback_port')
CALLBACK_URL = get_config_value('auth.callback_url')
AUTH_TIMEOUT = get_config_value('auth.auth_timeout')
POLLING_INTERVAL = get_config_value('auth.polling_interval')

def is_port_available(port: int) -> bool:
    """Check if a port is available."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except OSError:
            return False

def wait_for_server(port: int, timeout: int = 5) -> bool:
    """Wait for server to be ready."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if not is_port_available(port):
            return True
        time.sleep(0.1)
    return False

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback and store the verifier."""
    verifier = None
    
    def do_GET(self):
        """Handle GET request to callback URL."""
        if self.path.startswith('/callback'):
            # Parse the callback URL
            query = parse_qs(urlparse(self.path).query)
            OAuthCallbackHandler.verifier = query.get('oauth_verifier', [None])[0]
            logger.debug(f"Received OAuth callback with verifier: {OAuthCallbackHandler.verifier}")
            
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
        logger.info("\nTo use Twitter, you need to set up API credentials:")
        logger.info("1. Go to https://developer.twitter.com/en/portal/dashboard")
        logger.info("2. Create a new app or use an existing one")
        logger.info("3. Get your API Key (Consumer Key) and API Secret (Consumer Secret)")
        logger.info("4. In User authentication settings:")
        logger.info(f"   - Enable OAuth 1.0a")
        logger.info(f"   - Set callback URL to: {CALLBACK_URL}")
        logger.info("\nThen set them as environment variables:")
        logger.info("export TWITTER_CONSUMER_KEY='your_consumer_key'")
        logger.info("export TWITTER_CONSUMER_SECRET='your_consumer_secret'")
        logger.info("\nOr enter them now (they will be used only for this session):")
        consumer_key = input("Enter your Twitter API Key (Consumer Key): ").strip()
        consumer_secret = input("Enter your Twitter API Secret (Consumer Secret): ").strip()
    
    return consumer_key, consumer_secret

def start_callback_server() -> HTTPServer:
    """Start a local server to handle the OAuth callback."""
    if not is_port_available(CALLBACK_PORT):
        raise Exception(f"Port {CALLBACK_PORT} is already in use. Please choose a different port.")
    
    server = HTTPServer(('localhost', CALLBACK_PORT), OAuthCallbackHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    
    # Wait for server to be ready
    if not wait_for_server(CALLBACK_PORT):
        server.shutdown()
        raise Exception(f"Failed to start server on port {CALLBACK_PORT}")
    
    logger.debug(f"Callback server started on port {CALLBACK_PORT}")
    return server

def shutdown_server(server: HTTPServer, timeout: int = 5) -> None:
    """Shutdown the server with a timeout."""
    logger.info("Initiating server shutdown...")
    shutdown_start = time.time()
    
    # Create a thread to handle the shutdown
    def shutdown_thread():
        server.shutdown()
        server.server_close()
    
    shutdown_thread = threading.Thread(target=shutdown_thread)
    shutdown_thread.daemon = True
    shutdown_thread.start()
    
    # Wait for shutdown to complete with timeout
    shutdown_thread.join(timeout)
    if shutdown_thread.is_alive():
        logger.warning(f"Server shutdown timed out after {timeout} seconds")
    else:
        shutdown_time = time.time() - shutdown_start
        logger.info(f"Server shutdown completed in {shutdown_time:.2f} seconds")

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
        start_time = time.time()
        logger.info("Starting authentication process...")
        
        # Start callback server first
        logger.info("Starting local server to handle authentication...")
        server = start_callback_server()
        
        # Get Twitter API credentials
        logger.info("Getting Twitter credentials...")
        consumer_key, consumer_secret = get_twitter_credentials()
        
        # Initialize OAuth handler
        logger.info("Initializing OAuth handler...")
        auth = tweepy.OAuth1UserHandler(
            consumer_key, 
            consumer_secret,
            callback=CALLBACK_URL
        )
        
        try:
            # Get request token and authorization URL
            logger.info("Getting authorization URL...")
            redirect_url = auth.get_authorization_url()
            logger.info("Opening browser for Twitter authorization...")
            webbrowser.open(redirect_url)
            
            logger.info("Waiting for Twitter callback...")
            # Wait for callback with timeout
            callback_start_time = time.time()
            last_log_time = callback_start_time
            while not OAuthCallbackHandler.verifier:
                current_time = time.time()
                if current_time - callback_start_time > AUTH_TIMEOUT:
                    shutdown_server(server)
                    raise Exception("Authentication timed out. Please try again.")
                
                # Log progress every 5 seconds
                if current_time - last_log_time >= 5:
                    elapsed = int(current_time - callback_start_time)
                    logger.info(f"Still waiting for callback... ({elapsed}s elapsed)")
                    last_log_time = current_time
                
                time.sleep(POLLING_INTERVAL)
            
            callback_time = time.time() - callback_start_time
            logger.info(f"Received callback after {callback_time:.2f} seconds")
            
            # Shutdown server
            shutdown_server(server)
            
            # Exchange for access token
            logger.info("Exchanging verifier for access token...")
            token_start_time = time.time()
            auth.get_access_token(OAuthCallbackHandler.verifier)
            token_time = time.time() - token_start_time
            logger.info(f"Token exchange completed in {token_time:.2f} seconds")
            
            # Save tokens
            logger.info("Saving tokens...")
            save_start_time = time.time()
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
            save_time = time.time() - save_start_time
            logger.info(f"Tokens saved in {save_time:.2f} seconds")
            
            total_time = time.time() - start_time
            logger.info(f"Authentication successful! (took {total_time:.2f}s)")
            logger.info(f"Breakdown:")
            logger.info(f"- Callback wait time: {callback_time:.2f}s")
            logger.info(f"- Token exchange time: {token_time:.2f}s")
            logger.info(f"- Token save time: {save_time:.2f}s")
            logger.info(f"Tokens saved to {TOKEN_PATH}")
            
        except tweepy.TweepyException as e:
            shutdown_server(server)
            raise Exception(f"Failed to complete authentication: {e}")
            
    except Exception as e:
        raise Exception(f"Twitter login failed: {e}") 