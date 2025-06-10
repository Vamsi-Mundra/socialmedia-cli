"""Daily digest pipeline for generating tweet drafts."""
from pathlib import Path
from typing import List, Optional
from ..core.logging import get_logger
from ..collectors.web_search import collect
from ..writers.tweet_writer import draft, refine, rank
from ..drafts.manager import save
from ..llm.base import get_client
from ..core.errors import PipelineError

logger = get_logger("pipeline")

def run(
    topic: str,
    hours: int,
    tweets: int,
    chars: int,
    provider: str,
    model: str,
    out_dir: Optional[Path] = None
) -> Path:
    """Run the daily digest pipeline."""
    try:
        logger.info(f"Pipeline start: topic={topic}, hours={hours}, tweets={tweets}, chars={chars}, provider={provider}, model={model}")
        llm = get_client(provider, model)
        logger.info("LLM client initialized")
        bullets = collect(topic, hours, llm)
        logger.info(f"Collected {len(bullets)} bullets")
        drafts = draft(bullets, tweets, chars, llm)
        logger.info(f"Drafted {len(drafts)} tweets")
        refined = refine(drafts)
        logger.info(f"Refined {len(refined)} tweets")
        ranked = rank(refined, llm)
        logger.info(f"Ranked {len(ranked)} tweets")
        path = save("digest", topic, ranked, out_dir)
        logger.info(f"Saved digest to {path}")
        return path
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise PipelineError(f"Pipeline failed: {str(e)}") 