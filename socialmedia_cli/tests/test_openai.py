"""Test script for OpenAI integration."""
import os
import logging
import json
from rich import print as rprint
from rich.console import Console
from rich.logging import RichHandler
from ..llm import get_client

# Set up rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)

def test_openai_completion(
    prompt: str = "What is Python programming language?",
    model: str = "gpt-4.1",
    web_search: bool = True,
    response_length: str = "medium",
    temperature: float = 0.7
):
    """Test OpenAI completion with various parameters."""
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return
    
    console = Console()
    
    try:
        # Initialize client
        console.rule("[bold blue]Initializing OpenAI Client")
        llm = get_client(
            provider="openai",
            model=model,
            api_key=api_key
        )
        
        # Print request parameters
        console.rule("[bold green]Request Parameters")
        rprint({
            "prompt": prompt,
            "model": model,
            "web_search": web_search,
            "response_length": response_length,
            "temperature": temperature
        })
        
        # Generate response
        console.rule("[bold yellow]Generating Response")
        response = llm.generate(
            prompt=prompt,
            web_search=web_search,
            response_length=response_length,
            temperature=temperature
        )
        
        # Print response
        console.rule("[bold magenta]Response")
        rprint(response)
        
    except Exception as e:
        console.rule("[bold red]Error")
        console.print_exception()

def test_prompt_generation():
    """Test the prompt generation functionality."""
    console = Console()
    
    try:
        # Initialize client
        console.rule("[bold blue]Testing Prompt Generation")
        llm = get_client(
            provider="openai",
            model="gpt-4.1",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Test requirements
        requirements = {
            "num_tweets": 3,
            "length": "long",
            "style": "technical",
            "include_images": True,
            "tone": "professional",
            "target_audience": "developers"
        }
        
        # Generate prompt
        console.rule("[bold green]Generating Prompt")
        prompt = llm.generate_prompt(
            topic="npm incident",
            requirements=requirements
        )
        
        # Print generated prompt
        console.rule("[bold yellow]Generated Prompt")
        rprint(prompt)
        
        return prompt
        
    except Exception as e:
        console.rule("[bold red]Error")
        console.print_exception()
        return None

def test_tweet_generation(prompt: str):
    """Test the tweet generation functionality."""
    console = Console()
    
    try:
        # Initialize client
        console.rule("[bold blue]Testing Tweet Generation")
        llm = get_client(
            provider="openai",
            model="gpt-4.1",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Generate tweets
        console.rule("[bold green]Generating Tweets")
        tweets = llm.generate_tweets(
            prompt=prompt,
            num_tweets=3
        )
        
        # Print generated tweets
        console.rule("[bold yellow]Generated Tweets")
        rprint(tweets)
        
        return tweets
        
    except Exception as e:
        console.rule("[bold red]Error")
        console.print_exception()
        return None

def test_twitter_formatting(tweets):
    """Test the Twitter formatting functionality."""
    console = Console()
    
    try:
        # Initialize client
        console.rule("[bold blue]Testing Twitter Formatting")
        llm = get_client(
            provider="openai",
            model="gpt-4.1",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Format tweets
        console.rule("[bold green]Formatting Tweets")
        formatted_tweets = llm.format_for_twitter(tweets)
        
        # Print formatted tweets
        console.rule("[bold yellow]Formatted Tweets")
        rprint(formatted_tweets)
        
        return formatted_tweets
        
    except Exception as e:
        console.rule("[bold red]Error")
        console.print_exception()
        return None

def test_full_flow():
    """Test the complete tweet generation and formatting flow."""
    console = Console()
    
    try:
        # Initialize client
        console.rule("[bold blue]Testing Full Tweet Generation Flow")
        llm = get_client(
            provider="openai",
            model="gpt-4.1",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Test requirements
        requirements = {
            "num_tweets": 3,
            "length": "long",
            "style": "technical",
            "include_images": True,
            "tone": "professional",
            "target_audience": "developers"
        }
        
        # Generate and format tweets
        console.rule("[bold green]Generating and Formatting Tweets")
        formatted_tweets = llm.generate_and_post_tweets(
            topic="South Africa VS Australia World Test Chamipionship",
            requirements=requirements
        )
        
        # Print final formatted tweets
        console.rule("[bold yellow]Final Formatted Tweets")
        rprint(formatted_tweets)
        
        return formatted_tweets
        
    except Exception as e:
        console.rule("[bold red]Error")
        console.print_exception()
        return None

if __name__ == "__main__":
    # Test individual components
    console = Console()
    
    # Test prompt generation
    console.rule("[bold blue]Testing Prompt Generation")
    prompt = test_prompt_generation()
    
    if prompt:
        # Test tweet generation
        console.rule("[bold blue]Testing Tweet Generation")
        tweets = test_tweet_generation(prompt)
        
        if tweets:
            # Test Twitter formatting
            console.rule("[bold blue]Testing Twitter Formatting")
            formatted_tweets = test_twitter_formatting(tweets)
    
    # Test full flow
    console.rule("[bold blue]Testing Full Flow")
    final_tweets = test_full_flow() 