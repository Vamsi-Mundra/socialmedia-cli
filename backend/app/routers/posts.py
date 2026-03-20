from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from requests_oauthlib import OAuth1Session
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import Post, TwitterAccount, User
from ..schemas import (
    PostCreate,
    PostResponse,
    TopicOption,
    TweetDraftRequest,
    TweetDraftResponse,
)

router = APIRouter(prefix="/api/posts", tags=["posts"])

TOPIC_OPTIONS = [
    {
        "id": "product-launch",
        "label": "Product launch",
        "description": "Announce a launch, release, or shipping milestone.",
    },
    {
        "id": "industry-insight",
        "label": "Industry insight",
        "description": "Share a useful trend, lesson, or take from your niche.",
    },
    {
        "id": "customer-story",
        "label": "Customer story",
        "description": "Highlight a result, testimonial, or customer win.",
    },
    {
        "id": "productivity-tip",
        "label": "Productivity tip",
        "description": "Post a short tactical tip people can use right away.",
    },
    {
        "id": "event-promo",
        "label": "Event promo",
        "description": "Promote an event, webinar, or live session.",
    },
    {
        "id": "community-update",
        "label": "Community update",
        "description": "Invite followers to join the conversation or community.",
    },
]

TOPIC_TEMPLATES = {
    "product-launch": [
        "🚀 We just rolled out a fresh update around {topic}. It's built to save time, simplify the workflow, and help teams move faster. Curious what you'd automate first?",
        "Big milestone today: we're shipping new momentum around {topic}. Less friction, more clarity, and a smoother path from idea to execution. What feature matters most to you?",
    ],
    "industry-insight": [
        "One thing I'm watching closely in {topic}: the teams winning are the ones turning simple ideas into repeatable systems. Small improvements compound fast. What trend are you noticing?",
        "Quick insight on {topic}: consistency beats complexity. The strongest results usually come from clear messaging, fast feedback, and steady iteration. Agree or disagree?",
    ],
    "customer-story": [
        "A recent win from our {topic} work: focused execution made the biggest difference. When the process is clear, momentum follows. What's a customer result you're proud of this week?",
        "Nothing beats seeing progress in the real world. Our latest {topic} conversations reminded me that simple tools and timely follow-up still win. What's working best for your team?",
    ],
    "productivity-tip": [
        "Productivity tip for anyone working on {topic}: pick one metric, one deadline, and one next action before you start. Clear priorities make execution much easier. What's your go-to habit?",
        "Simple {topic} tip: draft fast, review once, then publish. Momentum often comes from reducing decisions, not adding more of them. What's your favorite productivity shortcut?",
    ],
    "event-promo": [
        "We're getting ready to talk all things {topic}. If you want practical ideas, live examples, and a chance to ask questions, keep an eye out for the full event details. Who should join us?",
        "Excited to share more about {topic} soon. We're planning a session packed with actionable takeaways, honest lessons, and room for discussion. Want the invite when it drops?",
    ],
    "community-update": [
        "The best part about building around {topic} is the community that forms around it. We're here to share ideas, learn in public, and help each other improve. What are you building right now?",
        "Quick community check-in on {topic}: what's one challenge you're solving this week? Sharing ideas openly helps everyone move faster, and I'd love to hear what you're working on.",
    ],
}


def _normalize_topic(topic: str) -> str:
    return " ".join(topic.replace("-", " ").split()).strip()


def _generate_tweet_text(topic: str) -> str:
    topic_key = topic.strip().lower()
    template_options = TOPIC_TEMPLATES.get(topic_key)
    normalized_topic = _normalize_topic(topic)

    if template_options is None:
        template_options = [
            "Here's a quick take on {topic}: the teams that stay consistent, listen closely, and keep shipping are the ones that build real momentum. What's your perspective?"
        ]

    template = template_options[sum(ord(char) for char in topic_key) % len(template_options)]
    text = template.format(topic=normalized_topic)
    if len(text) <= 280:
        return text
    return text[:277].rstrip() + "..."


@router.get("/topics", response_model=List[TopicOption])
def list_topics():
    return TOPIC_OPTIONS


@router.post("/generate", response_model=TweetDraftResponse)
def generate_tweet_draft(
    payload: TweetDraftRequest,
    current_user: User = Depends(get_current_user),
):
    return TweetDraftResponse(topic=payload.topic, content=_generate_tweet_text(payload.topic))


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

    content = _generate_tweet_text(post_data.topic or "") if post_data.auto_generate else (post_data.content or "").strip()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post content could not be generated.",
        )

    post = Post(user_id=current_user.id, content=content)

    try:
        tweet_id, tweet_url = _post_to_twitter(account, content)
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
