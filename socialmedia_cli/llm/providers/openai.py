"""OpenAI provider implementation with optional web-search support.

2025-06-13 – Patch 3
--------------------
* **generate_tweets** now *prepends a strict instruction block* that re-states:
  – tweet count, 550-700 character limit, 2-paragraph format  
  – mandatory `Source:` + `Image Prompt:` lines  
  – requirement to use the **latest available facts**  
  – JSON-only return schema  
  It also enables web-search by default so the model can pull real-time data.
* Other public APIs are unchanged.
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
        """Centralised call; adds hosted tool only when requested."""
        tools = [{"type": "web_search_preview"}] if web_search else None
        return self.client.responses.create(model=self.model, input=prompt, tools=tools)

    # ------------------------------------------------------------ Prompt builder
    def generate_prompt(
        self,
        topic: str,
        requirements: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Build a *second-level* prompt focussed on resources / context.
        Structure specifics are enforced later in `generate_tweets`.
        """
        base_prompt = f"""You are a social-media expert and compelling storyteller.

Write a prompt that will instruct **another LLM** to cover the live event
**{topic}** happening right now or happened today.

Your prompt must describe:

• The overall context & tone (real-time, professional-yet-quirky).  
• Where to pull facts regarding the **{topic}** happening right now or happened today.  
• """

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
    def generate_tweets(self, prompt: str, num_tweets: int = 1) -> List[Dict[str, str]]:
        """
        Execute the *tweet-writing* prompt, adding a strict instruction block so the
        model knows the exact format/length and to fetch the latest information.
        """
        instruction_block = f"""
================= TWEET OUTPUT REQUIREMENTS (READ CAREFULLY) =================

Write **exactly {num_tweets} tweets** that conform to ALL of these rules:

1. **Length:** 550-700 words each (≈ two short paragraphs). Do *not* exceed.
2. **Structure:**  
   Paragraph 1 – compelling hook / play-by-play.  
   Paragraph 2 – insight, analysis, or witty context.  
3. **Hashtags:** Weave 1-2 topical hashtags naturally into the body of each tweet.
4. **Freshness:** Use the *most up-to-date* information available right now.
5. **Output:** Return ONLY a valid JSON array, no markdown fences, like:

[
  {{ "text": "Tweet 1 exactly as above" }},
  {{ "text": "Tweet 2 …" }},
  {{ "text": "Tweet 3 …" }}
]

Any deviation will be considered a failure.
==============================================================================
"""
        full_prompt = f"{prompt}\n\n{instruction_block}"

        # Enable web-search so the model can fetch live facts
        resp = self._call_llm(full_prompt, web_search=True)
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
        hashtags: Sequence[str] = (),
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
        """Generic completion helper – routed through _call_llm for tool safety."""
        logger.info("Sending request to OpenAI API:")
        logger.info("Model: %s", self.model)
        logger.info("Prompt: %s...", prompt[:100])
        logger.info("Web search enabled: %s", web_search)

        response = self._call_llm(prompt, web_search=web_search)
        logger.info("Received response from OpenAI API.")
        return response
