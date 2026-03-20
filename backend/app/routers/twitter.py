import os
from typing import Dict

import tweepy
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, TwitterAccount
from ..schemas import TwitterConnectResponse, MessageResponse
from ..auth import get_current_user

router = APIRouter(prefix="/api/twitter", tags=["twitter"])

# In-memory store for OAuth request tokens (keyed by oauth_token)
_oauth_states: Dict[str, dict] = {}

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


def _get_twitter_keys() -> tuple[str, str]:
    consumer_key = os.getenv("TWITTER_CONSUMER_KEY", "")
    consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET", "")
    if not consumer_key or not consumer_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Twitter API credentials not configured. Set TWITTER_CONSUMER_KEY and TWITTER_CONSUMER_SECRET environment variables.",
        )
    return consumer_key, consumer_secret


@router.get("/connect", response_model=TwitterConnectResponse)
def connect_twitter(current_user: User = Depends(get_current_user)):
    consumer_key, consumer_secret = _get_twitter_keys()
    callback_url = os.getenv("TWITTER_CALLBACK_URL", "http://localhost:8000/api/twitter/callback")

    auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, callback=callback_url)
    try:
        authorize_url = auth.get_authorization_url()
    except tweepy.TweepyException as e:
        raise HTTPException(status_code=500, detail=f"Failed to get authorization URL: {e}")

    request_token = auth.request_token
    _oauth_states[request_token["oauth_token"]] = {
        "oauth_token_secret": request_token["oauth_token_secret"],
        "user_id": current_user.id,
        "consumer_key": consumer_key,
        "consumer_secret": consumer_secret,
    }

    return TwitterConnectResponse(authorize_url=authorize_url)


@router.get("/callback")
def twitter_callback(oauth_token: str, oauth_verifier: str, db: Session = Depends(get_db)):
    state = _oauth_states.pop(oauth_token, None)
    if not state:
        return RedirectResponse(url=f"{FRONTEND_URL}/dashboard?twitter=error&message=Invalid+OAuth+state")

    consumer_key = state["consumer_key"]
    consumer_secret = state["consumer_secret"]
    user_id = state["user_id"]

    auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret)
    auth.request_token = {
        "oauth_token": oauth_token,
        "oauth_token_secret": state["oauth_token_secret"],
    }

    try:
        access_token, access_token_secret = auth.get_access_token(oauth_verifier)
    except tweepy.TweepyException:
        return RedirectResponse(url=f"{FRONTEND_URL}/dashboard?twitter=error&message=Token+exchange+failed")

    # Fetch Twitter username
    twitter_username = None
    try:
        client = tweepy.Client(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
        )
        me = client.get_me()
        if me and me.data:
            twitter_username = me.data.username
    except Exception:
        pass

    existing = db.query(TwitterAccount).filter(TwitterAccount.user_id == user_id).first()
    if existing:
        existing.access_token = access_token
        existing.access_token_secret = access_token_secret
        existing.consumer_key = consumer_key
        existing.consumer_secret = consumer_secret
        existing.twitter_username = twitter_username
    else:
        account = TwitterAccount(
            user_id=user_id,
            access_token=access_token,
            access_token_secret=access_token_secret,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            twitter_username=twitter_username,
        )
        db.add(account)

    db.commit()
    return RedirectResponse(url=f"{FRONTEND_URL}/dashboard?twitter=connected")


@router.delete("/disconnect", response_model=MessageResponse)
def disconnect_twitter(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = db.query(TwitterAccount).filter(TwitterAccount.user_id == current_user.id).first()
    if not account:
        raise HTTPException(status_code=404, detail="No Twitter account connected")
    db.delete(account)
    db.commit()
    return MessageResponse(message="Twitter account disconnected")
