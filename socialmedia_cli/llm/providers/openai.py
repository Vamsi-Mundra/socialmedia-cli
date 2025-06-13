"""OpenAI provider implementation with web-enabled completion support."""
from typing import Dict, Any, List
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
        """Generate tweets using the provided prompt.
        
        Args:
            prompt: The prompt to use for tweet generation
            num_tweets: Number of tweets to generate
            
        Returns:
            List[Dict[str, str]]: List of tweets with their associated image prompts
        """
        try:
            response = self.client.responses.create(
                model=self.model,
                input=prompt,
                tools=[{"type": "web_search_preview"}]
            )
            logger.info(f"Response: {response}")
            
            # Find the message output in the response
            message_output = None
            for output in response.output:
                if hasattr(output, 'content'):
                    message_output = output
                    break
            
            if not message_output:
                raise Exception("No valid message output found in response")
                
            # Get the text content from the message
            content = message_output.content[0].text
            
            # Split content into tweets (for now using a simple approach)
            # TODO: Implement more sophisticated tweet parsing based on the actual response format
            tweets = []
            for i in range(num_tweets):
                tweets.append({
                    "text": f"Tweet {i+1}: {content[:240]}",  # Truncate to Twitter length
                    "image_prompt": f"Default image prompt for tweet {i+1}"
                })
            
            return tweets
            
        except Exception as e:
            logger.error(f"Error generating tweets: {str(e)}", exc_info=True)
            raise Exception(f"Tweet generation error: {str(e)}")

    def format_for_twitter(self, tweets: List[Dict[str, str]]) -> List[str]:
        """Format tweets for Twitter posting.
        
        Args:
            tweets: List of tweets with their associated image prompts
            
        Returns:
            List[str]: Formatted tweets ready for Twitter posting
        """
        formatted_tweets = []
        for tweet in tweets:
            # Format the tweet text and add any necessary metadata
            formatted_tweet = f"{tweet['text']}\n\n#tech #development"  # Add relevant hashtags
            formatted_tweets.append(formatted_tweet)
        return formatted_tweets

    def generate_and_post_tweets(self, topic: str, requirements: Dict[str, Any] = None) -> List[str]:
        """Generate and format tweets for a given topic.
        
        Args:
            topic: The topic to generate tweets about
            requirements: Additional requirements for the tweets
            
        Returns:
            List[str]: Formatted tweets ready for Twitter posting
        """
        try:
            # Step 1: Generate the prompt
            prompt = self.generate_prompt(topic, requirements)
            logger.info("Generated prompt successfully")
            
            # Step 2: Generate tweets using the prompt
            tweets = self.generate_tweets(prompt)
            logger.info(f"Generated {len(tweets)} tweets successfully")
            
            # Step 3: Format tweets for Twitter
            formatted_tweets = self.format_for_twitter(tweets)
            logger.info("Formatted tweets successfully")
            
            return formatted_tweets
            
        except Exception as e:
            logger.error(f"Error in generate_and_post_tweets: {str(e)}", exc_info=True)
            raise Exception(f"Tweet generation and formatting error: {str(e)}")

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
            print(response)
            return response
            
        except Exception as e:
            logger.error(f"Error in OpenAI API call: {str(e)}", exc_info=True)
            raise Exception(f"OpenAI API error: {str(e)}") 