"""Tweet writing and refinement utilities."""
from dataclasses import dataclass
from typing import List, Optional
import uuid

from ..llm.base import BaseLLM
from ..core.errors import WriterError

@dataclass
class DraftTweet:
    """A draft tweet with metadata."""
    id: str
    text: str
    score: Optional[float] = None
    reason: Optional[str] = None

def draft(bullets: List[str], n: int, chars: int, llm: BaseLLM) -> List[DraftTweet]:
    """Generate draft tweets from bullet points."""
    prompt = f"""Create {n} engaging tweets based on these bullet points:
    {chr(10).join(f"- {b}" for b in bullets)}
    
    Requirements:
    - Each tweet must be under {chars} characters
    - Include relevant hashtags
    - Make it engaging and informative
    - Format each tweet on a new line starting with "TWEET:"
    """
    
    try:
        response = llm.generate(prompt)
        tweets = []
        for line in response.split('\n'):
            if line.strip().startswith('TWEET:'):
                text = line[6:].strip()
                tweets.append(DraftTweet(
                    id=str(uuid.uuid4()),
                    text=text
                ))
        return tweets[:n]
    except Exception as e:
        raise WriterError(f"Failed to draft tweets: {str(e)}")

def refine(tweets: List[DraftTweet], local_llm: str = "ollama") -> List[DraftTweet]:
    """Refine tweets using a local LLM."""
    # TODO: Implement refinement logic
    return tweets

def rank(tweets: List[DraftTweet], llm: BaseLLM) -> List[DraftTweet]:
    """Rank tweets by quality and engagement potential."""
    prompt = f"""Rate these tweets on a scale of 0-1 for quality and engagement:
    {chr(10).join(f"{i+1}. {t.text}" for i, t in enumerate(tweets))}
    
    For each tweet, provide:
    1. A score (0-1)
    2. A brief reason for the score
    
    Format each response as "TWEET {i+1}: SCORE {score} - {reason}"
    """
    
    try:
        response = llm.generate(prompt)
        for line in response.split('\n'):
            if line.startswith('TWEET'):
                parts = line.split(':')
                if len(parts) == 2:
                    idx = int(parts[0].split()[1]) - 1
                    score_parts = parts[1].split('-')
                    if len(score_parts) == 2 and idx < len(tweets):
                        score = float(score_parts[0].split()[-1])
                        reason = score_parts[1].strip()
                        tweets[idx].score = score
                        tweets[idx].reason = reason
        
        return sorted(tweets, key=lambda t: t.score or 0, reverse=True)
    except Exception as e:
        raise WriterError(f"Failed to rank tweets: {str(e)}") 