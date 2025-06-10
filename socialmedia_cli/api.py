"""
Central API dispatcher for different social media platforms.
"""

from .components import twitter

def post(platform: str, text: str) -> tuple[str, str]:
    """
    Post a message to the specified platform.
    
    Args:
        platform: The platform to post to (e.g., 'twitter')
        text: The message to post
        
    Returns:
        Tuple of (post_id, post_url)
        
    Raises:
        ValueError: If the platform is not supported
    """
    if platform == "twitter":
        return twitter.post_tweet(text)
    else:
        raise ValueError(f"Unsupported platform: {platform}") 