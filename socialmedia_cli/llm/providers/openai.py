"""OpenAI provider implementation with web-enabled completion support."""
from typing import Dict, Any, List, Union, Sequence, Optional
import logging
import json
import re
from openai import OpenAI
from ..base import BaseLLM, register

# Set up logging
logger = logging.getLogger(__name__)

@register("openai")
class OpenAILLM(BaseLLM):
    """OpenAI API provider with web search capability."""
    
    def __init__(self, model: str, api_key: str = None, **kwargs):
        super().__init__(model, **kwargs)
        self.client = OpenAI(api_key=api_key)
        logger.info(f"Initialized OpenAI client with model: {model}")
    
    def generate_prompt(self, topic: str, requirements: Dict[str, Any] = None) -> str:
        """Generate a prompt for tweet generation.
        
        Args:
            topic: The topic to generate tweets about
            requirements: Additional requirements for the prompt (e.g., length, style, etc.)
            
        Returns:
            str: A well-structured prompt for tweet generation
        """
        try:
            base_prompt = f"""You are a social media expert and a compelling storyteller. Create a detailed prompt for generating tweets about: {topic}. The {topic} is a live event that is happening in the current world. 

The prompt should:
1. Set the context and tone
2. Specify the number of tweets needed
3. What all current real world resources it needs to go through to generate tweet about this {topic}.
3. Define the structure and length requirements
4. Include any specific style guidelines
5. Request image prompts if needed

Format the prompt in a way that can be directly used by another LLM to generate the actual tweets."""

            if requirements:
                base_prompt += "\n\nAdditional Requirements:\n" + json.dumps(requirements, indent=2)

            response = self.client.responses.create(
                model=self.model,
                input=base_prompt,
                tools=[{"type": "web_search_preview"}]
            )
            
            return response.output[0].content[0].text
            
        except Exception as e:
            logger.error(f"Error generating prompt: {str(e)}", exc_info=True)
            raise Exception(f"Prompt generation error: {str(e)}")

    def generate_tweets(self, prompt: str, num_tweets: int = 3) -> List[Dict[str, str]]:
        """
        Call the LLM, parse a JSON array if present, otherwise fall back to
        Markdown parsing that is resilient to extra new-lines and *Alt-text:* blocks.
        """
        logger = logging.getLogger(__name__)

        resp = self.client.responses.create(
            model=self.model,
            input=prompt,
            tools=[{"type": "web_search_preview"}],
        )
        assistant_msg = next(
            (o for o in resp.output if getattr(o, "type", "") == "message"), None
        )
        if assistant_msg is None:
            raise RuntimeError("Missing assistant message in LLM response")

        raw = assistant_msg.content[0].text.strip()

        # ---------- 1) JSON path ----------
        try:
            cleaned = re.sub(r"^\s*```(?:json)?|```$", "", raw, flags=re.I | re.M).strip()
            tweets = json.loads(cleaned)
            if not isinstance(tweets, list):
                raise ValueError
        except Exception:
            # ---------- 2) Markdown fallback ----------
            block_regex = re.compile(
                r"\*\*Tweet\s+\d+:\*\*\s*"                          # "**Tweet 1:**"
                r"(?P<body>.*?)"                                    #   tweet text
                r"(?:\n\*Image prompt:\s*(?P<img>.*?)\*)?"          # *Image prompt: …*
                r"(?:\n\*Alt-text:\s*(?P<alt>.*?)\*)?"              # *Alt-text: …*  (optional)
                r"(?=\n\*\*Tweet\s+\d+:|\Z)",                       # look-ahead for next "**Tweet" or end
                re.S | re.I,
            )
            tweets = [
                {
                    "text": m.group("body").strip(),
                    "image_prompt": (m.group("img") or "").strip(),
                    "alt_text": (m.group("alt") or "").strip(),
                }
                for m in block_regex.finditer(raw)
            ]

        # ---------- 3) Normalise + truncate ----------
        cleaned: List[Dict[str, str]] = []
        for t in tweets[:num_tweets]:
            text = t.get("text", "").strip()
            if len(text) > 280:
                text = text[:277] + "…"
            cleaned.append(
                {
                    "text": text,
                    "image_prompt": t.get("image_prompt") or None,
                    "alt_text": t.get("alt_text") or None,
                }
            )
        if not cleaned:
            raise RuntimeError("No tweets parsed from LLM output")
        return cleaned

    def format_for_twitter(
        self,
        tweets: List[Dict[str, str]],
        hashtags: Optional[Sequence[str]] = ("tech", "development"),
    ) -> List[str]:
        """
        Build final tweet bodies.  Hashtags can be a list/tuple or None.

        • Ensures each hashtag starts with '#'.
        • Skips tweets whose text is empty after parsing.
        • Re-truncates if tags push length > 280.
        """
        tag_block = ""
        if hashtags:
            tag_block = " ".join(
                f"#{tag.lstrip('#')}" for tag in hashtags if tag
            ).strip()

        result = []
        for t in tweets:
            body = t["text"].strip()
            if not body:
                continue  # defensive: ignore blanks

            full = f"{body}"
            if tag_block:
                full += f"\n\n{tag_block}"

            if len(full) > 280:
                # keep room for newline + tags
                room = 280 - (len(tag_block) + 2 if tag_block else 0)
                full = f"{body[: room - 1]}…"
                if tag_block:
                    full += f"\n\n{tag_block}"

            result.append(full)

        return result

    def generate_and_post_tweets(
        self,
        topic: str,
        requirements: Union[Dict[str, Any], None] = None,
        num_tweets: int = 3,
    ) -> List[str]:
        """
        1. Build an LLM prompt (self.generate_prompt does not change).
        2. Generate `num_tweets` tweets.
        3. Format for posting.
        """
        try:
            prompt = self.generate_prompt(topic, requirements)
            logger.info("Generated prompt: %s", prompt)

            tweets = self.generate_tweets(prompt, num_tweets=num_tweets)
            logger.info("Generated %d tweets: %s", len(tweets), json.dumps(tweets, indent=2))

            formatted = self.format_for_twitter(tweets)
            logger.info("Formatted tweets: %s", json.dumps(formatted, indent=2))
            return formatted

        except Exception as e:
            logger.exception("generate_and_post_tweets failed: %s", str(e))
            raise

    def generate(
        self,
        prompt: str,
        web_search: bool = False,
        response_length: str = "medium",
        **kwargs
    ) -> str:
        """Generate text from a prompt using OpenAI's completion API.
        
        Args:
            prompt: The input prompt
            web_search: Whether to enable OpenAI's web search capability
            response_length: Length of response - "short" (~50 words), "medium" (~200 words), "long" (~500 words)
            **kwargs: Additional parameters for the API
        """
        try:
            # Log request parameters
            logger.info(f"Sending request to OpenAI API:")
            logger.info(f"Model: {self.model}")
            logger.info(f"Prompt: {prompt[:100]}...")  # Log first 100 chars of prompt
            logger.info(f"Web search enabled: {web_search}")
            
            # Create completion request
            tools = [{"type": "web_search_preview"}] if web_search else None
            response = self.client.responses.create(
                model=self.model,
                input=prompt,
                tools=tools,      
            )
            
            # Log response details
            logger.info("Received response from OpenAI API:")
            logger.info(json.dumps(response, indent=2))
            return response
            
        except Exception as e:
            logger.error(f"Error in OpenAI API call: {str(e)}", exc_info=True)
            raise Exception(f"OpenAI API error: {str(e)}") 