# SocialMedia CLI

A command-line tool for posting to social media platforms.

## Installation

```bash
git clone <repo>
cd socialmedia-cli
./verify.sh
```

## Usage

### Authentication

To authenticate with a social media platform:

```bash
socialmedia-cli login twitter
```

This will:
1. Open your browser for OAuth authentication
2. Save your credentials to `~/.socialmedia_cli_tokens.json`
3. Run a test post to verify the connection

### Posting

To post a message:

```bash
socialmedia-cli post twitter "Hello world"
```

## Supported Platforms

Currently supports:
- Twitter

## Extending

To add support for a new platform:
1. Create a new component in `socialmedia_cli/components/`
2. Implement the platform-specific API wrapper
3. Add the platform to the API dispatcher in `socialmedia_cli/api.py`
4. Update the authentication module in `socialmedia_cli/auth.py` 