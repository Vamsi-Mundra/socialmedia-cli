"""OpenAI provider implementation with optional web-search support.

2025-06-13 – Patch
------------------
* Fixes 400 error when model does not support the hosted *web_search_preview* tool.
* Makes LLM parsing reliable by forcing the nested prompt to ask for **strict JSON**.
* Changes tweet size requirement to **550-700 characters** (was “600-700 words”).
* Keeps every public method & external behaviour unchanged.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional, Sequence

from openai import OpenAI

from ..base import BaseLLM, register

logger = logging.getLogger(__name__)


# ─────────────────────────────── Helpers ──────────────────────────────────────
def _strip_json_fence(text: str) -> str:
    """Remove ``` and ```json fences if present."""
    return re.sub(r"^\s*```(?:json)?|```$", "", text, flags=re.I | re.M).strip()


# ─────────────────────────────── Provider ─────────────────────────────────────
@register("openai")
class OpenAILLM(BaseLLM):
    """OpenAI API provider with optional web-search capability."""

    # --------------------------------------------------------------------- init
    def __init__(self, model: str, api_key: str | None = None, **kwargs):
        super().__init__(model, **kwargs)
        self.client = OpenAI(api_key=api_key)
        logger.info("Initialized OpenAI client with model: %s", model)

    # ---------------------------------------------------------------- LL helpers
    def _call_llm(self, prompt: str, *, web_search: bool = False):
        """Centralised call so ‘tools’ logic lives in one place."""
        tools = [{"type": "web_search_preview"}] if web_search else None
        return self.client.responses.create(model=self.model, input=prompt, tools=tools)

    # ------------------------------------------------------------ Prompt builder
    def generate_prompt(
        self,
        topic: str,
        requirements: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Return a *second-level* prompt that another LLM will use to write tweets.

        Key guarantees:
        • Exactly 3 tweets, each **550-700 characters**.
        • The tweet-writing LLM must answer with *only* a JSON list like:
          [
            { "text": "…" },
            { "text": "…" },
            { "text": "…" }
          ]
        """
        base_prompt = f"""You are a social-media expert and compelling storyteller.

Your task: write a prompt that will instruct **another LLM** to draft **exactly 3 tweets**
about the live event **{topic}** happening right now.

The prompt you output **must**:

1. **Set context & tone** – live, real-time, voice = professional yet quirky.
2. **Specify number of tweets** – exactly three.
3. **List real-world resources** – live scorecards, official feeds, hashtags, etc.
4. **Define structure & length** – each tweet must be **550-700 characters** long
   (≈ two short paragraphs, thread-style, readable).
5. **Include style guidelines** – 1-2 topical hashtags already inside each tweet,
   vivid metaphors, avoid clichés.
6. **Ask for an `Image Prompt:` line** after every tweet describing a fitting graphic.
7. **Output format** – instruct the LLM to answer with **only** a valid JSON array:
[
  {{ "text": "first tweet 550-700 chars…" }},
  {{ "text": "second tweet 550-700 chars…" }},
  {{ "text": "third tweet 550-700 chars…" }}
]
No markdown fences, no extra keys, no commentary."""

        if requirements:
            base_prompt += (
                "\n\n### Additional User Requirements\n"
                + json.dumps(requirements, indent=2)
            )

        resp = self._call_llm(base_prompt, web_search=False)
        prompt_text = resp.output[0].content[0].text.strip()
        logger.debug("Generated nested prompt:\n%s", prompt_text)
        return prompt_text

    # ------------------------------------------------------------ Tweet creator
    def generate_tweets(self, prompt: str, num_tweets: int = 3) -> List[Dict[str, str]]:
        """Call the LLM and return `[{{'text': …}}, …]`."""
        resp = self._call_llm(prompt, web_search=False)
        msg = next((o for o in resp.output if getattr(o, "type", "") == "message"), None)
        if msg is None:
            raise RuntimeError("No assistant message in LLM response")

        raw = msg.content[0].text.strip()

        # 1️⃣  JSON path (preferred)
        try:
            tweets = json.loads(_strip_json_fence(raw))
            if not isinstance(tweets, list):
                raise ValueError
        except Exception:
            # 2️⃣  Markdown fallback (**Tweet 1:** …)
            block_rx = re.compile(
                r"\*\*Tweet\s+\d+:\*\*\s*(?P<body>.*?)"
                r"(?:\n\*Image prompt:.*|\n\*Alt-text:.*|$)",
                re.S | re.I,
            )
            tweets = [{"text": m.group("body").strip()} for m in block_rx.finditer(raw)]

        # 3️⃣  Final clean-up
        for t in tweets:
            t["text"] = t["text"].strip().strip('"\u201c\u201d')

        if not tweets:
            raise RuntimeError("Could not extract tweets from LLM output")

        return tweets[:num_tweets]

    # ------------------------------------------------------------ Formatter
    def format_for_twitter(
        self,
        tweets: List[Dict[str, str]],
        hashtags: Sequence[str] = ("tech", "development"),
    ) -> List[str]:
        tag_block = " ".join(f"#{tag.lstrip('#')}" for tag in hashtags)
        return [f"{t['text'].rstrip()}\n\n{tag_block}" for t in tweets if t["text"].rstrip()]

    # --------------------------------------------------------- High-level flow
    def generate_and_post_tweets(
        self,
        topic: str,
        requirements: Optional[Dict[str, Any]] = None,
        num_tweets: int = 3,
    ) -> List[str]:
        prompt = self.generate_prompt(topic, requirements)
        logger.info("Generated prompt: %s", prompt)

        tweets = self.generate_tweets(prompt, num_tweets=num_tweets)
        logger.info("Generated %d tweets: %s", len(tweets), json.dumps(tweets, indent=2))

        formatted = self.format_for_twitter(tweets)
        logger.info("Formatted tweets: %s", json.dumps(formatted, indent=2))
        return formatted

    # ------------------------------------------------------------- Generic gen
    def generate(
        self,
        prompt: str,
        web_search: bool = False,
        response_length: str = "medium",
        **kwargs,
    ):
        """
        Generic completion helper (unchanged), but routed through _call_llm
        so that hosted tool is added only when requested.
        """
        logger.info("Sending request to OpenAI API:")
        logger.info("Model: %s", self.model)
        logger.info("Prompt: %s...", prompt[:100])
        logger.info("Web search enabled: %s", web_search)

        response = self._call_llm(prompt, web_search=web_search)
        logger.info("Received response from OpenAI API.")
        return response
