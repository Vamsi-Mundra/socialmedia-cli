from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from requests_oauthlib import OAuth1Session
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Post, TwitterAccount
from ..schemas import PostCreate, PostResponse
from ..auth import get_current_user

router = APIRouter(prefix="/api/posts", tags=["posts"])


def _post_to_twitter(account: TwitterAccount, text: str) -> tuple[str, str]:
    """Post a tweet using stored OAuth credentials, reusing CLI logic."""
    oauth = OAuth1Session(
        account.consumer_key,
        client_secret=account.consumer_secret,
        resource_owner_key=account.access_token,
        resource_owner_secret=account.access_token_secret,
    )
    response = oauth.post("https://api.twitter.com/2/tweets", json={"text": text})

    if response.status_code != 201:
        raise ValueError(f"Twitter API error: {response.status_code} {response.text}")

    data = response.json()
    if not data or "data" not in data:
        raise ValueError("Invalid response from Twitter API")

    tweet_id = data["data"]["id"]
    username = account.twitter_username or "i"
    tweet_url = f"https://x.com/{username}/status/{tweet_id}"
    return tweet_id, tweet_url


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = (
        db.query(TwitterAccount)
        .filter(TwitterAccount.user_id == current_user.id)
        .first()
    )
    if not account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Twitter account connected. Please connect your account first.",
        )

    post = Post(user_id=current_user.id, content=post_data.content)

    try:
        tweet_id, tweet_url = _post_to_twitter(account, post_data.content)
        post.tweet_id = tweet_id
        post.tweet_url = tweet_url
        post.status = "posted"
    except Exception as e:
        post.status = "failed"
        post.error_message = str(e)

    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.get("", response_model=List[PostResponse])
def list_posts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    posts = (
        db.query(Post)
        .filter(Post.user_id == current_user.id)
        .order_by(Post.created_at.desc())
        .all()
    )
    return posts
