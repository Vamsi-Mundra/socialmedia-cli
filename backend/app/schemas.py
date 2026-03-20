from pydantic import BaseModel, model_validator
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: str
    name: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    twitter_connected: bool = False
    twitter_username: Optional[str] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class PostCreate(BaseModel):
    content: Optional[str] = None
    topic: Optional[str] = None
    auto_generate: bool = False

    @model_validator(mode="after")
    def validate_payload(self):
        if self.auto_generate and not self.topic:
            raise ValueError("Topic is required when automatic tweet generation is enabled")
        if not self.auto_generate and not (self.content and self.content.strip()):
            raise ValueError("Content is required when automatic tweet generation is disabled")
        return self


class PostResponse(BaseModel):
    id: int
    content: str
    tweet_id: Optional[str] = None
    tweet_url: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TopicOption(BaseModel):
    id: str
    label: str
    description: str


class TweetDraftRequest(BaseModel):
    topic: str


class TweetDraftResponse(BaseModel):
    topic: str
    content: str


class TwitterConnectResponse(BaseModel):
    authorize_url: str


class MessageResponse(BaseModel):
    message: str
