"""Tweet draft management utilities."""
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from ..core.storage import save_jsonl, load_jsonl
from ..writers.tweet_writer import DraftTweet

DRAFTS_DIR = Path.home() / ".socialmedia_cli_drafts"
DRAFTS_DIR.mkdir(parents=True, exist_ok=True)

def save(category: str, topic: str, tweets: List[DraftTweet], out_dir: Optional[Path] = None) -> Path:
    """Save draft tweets to a JSONL file."""
    if out_dir is None:
        out_dir = DRAFTS_DIR
    
    timestamp = datetime.now().strftime("%Y-%m-%d")
    filename = f"{category}_{topic}_{timestamp}.jsonl"
    path = out_dir / filename
    
    records = [
        {
            "id": t.id,
            "text": t.text,
            "score": t.score,
            "reason": t.reason
        }
        for t in tweets
    ]
    
    save_jsonl(path, records)
    return path

def list_drafts(category: Optional[str] = None) -> List[Path]:
    """List available draft files."""
    pattern = f"{category}_*.jsonl" if category else "*.jsonl"
    return sorted(DRAFTS_DIR.glob(pattern))

def load(path: Path) -> List[DraftTweet]:
    """Load draft tweets from a JSONL file."""
    records = load_jsonl(path)
    return [
        DraftTweet(
            id=r["id"],
            text=r["text"],
            score=r.get("score"),
            reason=r.get("reason")
        )
        for r in records
    ] 