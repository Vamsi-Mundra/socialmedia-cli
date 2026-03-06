# Social Media CLI Usage Guide

## Setup

1. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Install dependencies (if not already done):**
   ```bash
   pip install -e .
   pip install tweepy
   ```

## Available Commands

### 1. Login to Social Media Platform
**Purpose:** Authenticate with Twitter (or other platforms)
```bash
# Using CLI (may have compatibility issues)
socialmedia-cli login twitter

# Using direct Python (recommended)
python -c "from socialmedia_cli.auth import login; login('twitter')"
```

### 2. Post a Tweet
**Purpose:** Post a message directly to Twitter
```bash
# Using CLI (may have compatibility issues)
socialmedia-cli post-text twitter "Your tweet message here"

# Using direct Python (recommended)
python -c "from socialmedia_cli.api import post; post('twitter', 'Your tweet message here')"
```

### 3. Generate Daily Digest
**Purpose:** Generate AI-powered tweet summaries for a topic
```bash
# Using CLI (may have compatibility issues)
socialmedia-cli digest "AI news" --hours 24 --tweets 5 --chars 280

# Using direct Python (recommended)
python -c "from socialmedia_cli.pipelines.daily_digest import run; run('AI news', 24, 5, 280)"
```

### 4. List Draft Files
**Purpose:** View available draft tweets
```bash
# Using CLI (may have compatibility issues)
socialmedia-cli drafts digest

# Using direct Python (recommended)
python -c "from socialmedia_cli.drafts.manager import list_drafts; print(list_drafts('digest'))"
```

### 5. Post Draft (Not Implemented)
**Purpose:** Post a saved draft tweet
```bash
# This feature is not yet implemented
socialmedia-cli post <draft_id>
```

## Quick Start Example

1. **First time setup:**
   ```bash
   source venv/bin/activate
   python -c "from socialmedia_cli.auth import login; login('twitter')"
   ```

2. **Post your first tweet:**
   ```bash
   python -c "from socialmedia_cli.api import post; post('twitter', 'Hello from Social Media CLI!')"
   ```

3. **Generate and post a digest:**
   ```bash
   python -c "from socialmedia_cli.pipelines.daily_digest import run; run('tech news', 24, 3, 280)"
   ```

## Troubleshooting

### CLI Compatibility Issues
The CLI has compatibility issues with the current typer version. Use the direct Python approach instead:

```bash
# Instead of: socialmedia-cli login twitter
# Use: python -c "from socialmedia_cli.auth import login; login('twitter')"

# Instead of: socialmedia-cli post-text twitter "message"
# Use: python -c "from socialmedia_cli.api import post; post('twitter', 'message')"
```

### Missing Dependencies
If you get import errors, install missing packages:
```bash
pip install tweepy requests typer pydantic tomli
```

## Configuration

The tool uses configuration files for defaults. Check the `socialmedia_cli/core/config.py` file for available settings.

## Supported Platforms

Currently supports:
- Twitter (via Tweepy)

## File Structure

- `socialmedia_cli/auth.py` - Authentication logic
- `socialmedia_cli/api.py` - API posting logic
- `socialmedia_cli/components/twitter.py` - Twitter-specific implementation
- `socialmedia_cli/pipelines/daily_digest.py` - AI digest generation
- `socialmedia_cli/drafts/manager.py` - Draft management 