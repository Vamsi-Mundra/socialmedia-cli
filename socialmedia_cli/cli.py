"""
Command-line interface for the social media CLI tool.
"""

import argparse
import sys
from typing import Optional
from . import auth, api
import typer
from pathlib import Path
from .core.logging import get_logger

from .pipelines.daily_digest import run
from .drafts.manager import list_drafts, load

class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(1, f"error: {message}\n")

def main(args: Optional[list[str]] = None) -> int:
    """Main entry point for the CLI."""
    parser = CustomArgumentParser(description="Post to social media platforms from the command line")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Login command
    login_parser = subparsers.add_parser("login", help="Authenticate with a social media platform")
    login_parser.add_argument("platform", help="Platform to authenticate with (e.g., twitter)")

    # Post command
    post_parser = subparsers.add_parser("post", help="Post a message to a social media platform")
    post_parser.add_argument("platform", help="Platform to post to (e.g., twitter)")
    post_parser.add_argument("message", help="Message to post")

    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        parser.print_help()
        return 1

    if parsed_args.command == "login":
        auth.login(parsed_args.platform)
        return 0
    elif parsed_args.command == "post":
        api.post(parsed_args.platform, parsed_args.message)
        return 0
    else:
        parser.print_help()
        return 1

app = typer.Typer()
logger = get_logger("cli")

@app.command()
def login(
    platform: str = typer.Argument(..., help="Platform to authenticate with (e.g., twitter)")
):
    """Authenticate with a social media platform."""
    logger.info(f"Login command called for platform={platform}")
    try:
        auth.login(platform)
        typer.echo(f"Successfully logged in to {platform}")
        logger.info(f"Successfully logged in to {platform}")
    except Exception as e:
        logger.error(f"Login failed: {e}")
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)

@app.command()
def post_text(
    platform: str = typer.Argument(..., help="Platform to post to (e.g., twitter)"),
    message: str = typer.Argument(..., help="Message to post")
):
    """Post a message directly to a social media platform."""
    logger.info(f"Post command called for platform={platform}")
    try:
        api.post(platform, message)
        typer.echo(f"Successfully posted to {platform}")
        logger.info(f"Successfully posted to {platform}")
    except Exception as e:
        logger.error(f"Post failed: {e}")
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)

@app.command()
def digest(
    topic: str = typer.Argument(..., help="Topic to generate digest for"),
    hours: int = typer.Option(24, help="Hours to look back"),
    tweets: int = typer.Option(5, help="Number of tweets to generate"),
    chars: int = typer.Option(240, help="Maximum characters per tweet"),
    provider: str = typer.Option("groq", help="LLM provider to use"),
    model: str = typer.Option("mixtral-8x7b-internet", help="LLM model to use")
):
    """Generate a daily digest of tweets for a topic."""
    logger.info(f"Starting digest: topic={topic}, hours={hours}, tweets={tweets}, chars={chars}, provider={provider}, model={model}")
    try:
        path = run(topic, hours, tweets, chars, provider, model)
        typer.echo(f"Generated digest at: {path}")
        logger.info(f"Digest generated at: {path}")
    except Exception as e:
        logger.error(f"Digest failed: {e}")
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)

@app.command()
def drafts(
    category: Optional[str] = typer.Argument(None, help="Category to list (e.g. 'digest')")
):
    """List available draft files."""
    logger.info(f"Listing drafts for category: {category}")
    try:
        files = list_drafts(category)
        if not files:
            typer.echo("No drafts found")
            logger.info("No drafts found")
            return
        for file in files:
            typer.echo(file.name)
        logger.info(f"Listed {len(files)} drafts")
    except Exception as e:
        logger.error(f"Drafts list failed: {e}")
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)

@app.command()
def post(
    draft_id: str = typer.Argument(..., help="ID of draft to post")
):
    """Post a draft tweet."""
    logger.info(f"Post command called for draft_id={draft_id}")
    # TODO: Implement posting logic
    typer.echo("Posting not implemented yet")
    logger.warning("Posting not implemented yet")

if __name__ == "__main__":
    app() 