"""
Command-line interface for the social media CLI tool.
"""

import argparse
import sys
from typing import Optional
from . import auth, api

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

if __name__ == "__main__":
    sys.exit(main()) 