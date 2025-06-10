# SocialMedia-CLI Project Work Items

Each item below represents a unit of work. Once all criteria are met, the feature is done.

---

## 1. Project Boilerplate & Entry Point

**Work Item:**  
- Scaffold a Python package named `socialmedia_cli`

**Acceptance Criteria:**  
- Directory tree exactly as below:  
```

socialmedia-cli/
WORK\_ITEMS.md
README.md
setup.py
requirements.txt
verify.sh
socialmedia\_cli/
**init**.py
cli.py
components/
**init**.py
twitter.py
auth.py
api.py
tests/
**init**.py
test\_cli.py
test\_auth.py
test\_twitter.py

````
- `setup.py` defines an entry point:
```py
entry_points={
    'console_scripts': [
        'socialmedia-cli=socialmedia_cli.cli:main'
    ]
}
````

* `requirements.txt` lists at minimum `tweepy`, `pytest`, `pytest-mock`.

---

## 2. Core CLI & Subcommand Routing

**Work Item:**

* Implement `cli.py` to route subcommands

**Acceptance Criteria:**

* Uses `argparse` to define two top-level commands:

  1. `login <platform>`
  2. `post <platform> <message>`
* Running `socialmedia-cli --help` shows both commands with brief descriptions.
* Invalid commands exit with code `1` and print a usage hint.

---

## 3. OAuth & Token Storage (`auth.py`)

**Work Item:**

* Abstract OAuth 1.0a flow into `auth.py`

**Acceptance Criteria:**

* Function `login(platform: str)` that:

  * Retrieves request token via Tweepy for the given `platform` (only `twitter` initially).
  * Prints authorization URL; prompts for `oauth_verifier`.
  * Exchanges for `access_token` & `access_token_secret`.
  * Writes JSON to `~/.socialmedia_cli_tokens.json` with file mode `0o600`.
* After saving tokens, waits 60 s and then triggers a “smoke test” via the platform’s post function (see Twitter item below).
* Raises a descriptive exception if the platform is unsupported or network errors occur.

---

## 4. Twitter Component (`components/twitter.py`)

**Work Item:**

* Build Twitter-specific API wrapper

**Acceptance Criteria:**

* Function `post_tweet(text: str) -> Tuple[str, str]` that:

  * Reads tokens from `~/.socialmedia_cli_tokens.json`.
  * Authenticates with Tweepy using OAuth 1.0a.
  * Posts `text`.
  * Returns `(tweet_id, tweet_url)`.
* Errors on missing/revoked tokens with clear messages.
* Utilizes `api = tweepy.API(auth)` and `status = api.update_status(text)`.

---

## 5. API Dispatcher (`api.py`)

**Work Item:**

* Central routing for different platforms

**Acceptance Criteria:**

* Function `post(platform: str, text: str)` that:

  * Calls the correct component (`twitter.post_tweet`) based on `platform`.
  * Raises if platform not implemented.

---

## 6. Unit Tests

**Work Item:**

* Create isolated, mocked tests under `/tests`

**Acceptance Criteria:**

* **`test_auth.py`**

  * Mocks Tweepy OAuth handlers to verify request-token flow.
  * Asserts `~/.socialmedia_cli_tokens.json` is written correctly.
  * Mocks a 60 s delay and verifies a “Hello to my workld!!” post.
* **`test_twitter.py`**

  * Mocks `tweepy.API` to simulate `update_status`.
  * Verifies `post_tweet` returns correct `(id, url)`.
  * Simulates invalid tokens and asserts exception.
* **`test_cli.py`**

  * Uses `subprocess` or `pytest`’s `capsys` to run `socialmedia-cli login twitter` and `socialmedia-cli post twitter "msg"`.
  * Confirms exit codes and output formatting.

---

## 7. Continuous Verification Script

**Work Item:**

* Provide `verify.sh` to build & test

**Acceptance Criteria:**

* Script steps:

  1. `python3 -m venv .venv`
  2. `source .venv/bin/activate`
  3. `pip install -r requirements.txt`
  4. `pip install -e .`
  5. `pytest --maxfail=1 --disable-warnings -q`
* Exits zero only on full success.
* Prints “✅ All checks passed” at end.

---

## 8. Documentation (`README.md`)

**Work Item:**

* Write end-to-end instructions

**Acceptance Criteria:**

* Shows **Installation**:

  ```bash
  git clone <repo>
  cd socialmedia-cli
  ./verify.sh
  ```
* **Usage** examples:

  * `socialmedia-cli login twitter`
  * `socialmedia-cli post twitter "Hello world"`
* Explains token file location and how to extend to other platforms.

---

When all items are green-lit, the project is complete, fully tested, and self-verifiable via `verify.sh`.
