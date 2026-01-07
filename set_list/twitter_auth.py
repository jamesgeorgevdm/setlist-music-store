"""
twitter_auth.py

Handles OAuth1-based authentication with the Twitter API and provides
a client for posting tweets (with optional media upload) from the app.

Saves and restores session tokens locally to avoid repeated logins.
"""

import os
import json
from requests_oauthlib import OAuth1Session

# Twitter API credentials (You should ideally load these from environment variables in production)
CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")

# Token file location (stored within the Django app directory)
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "twitter_tokens.json")


class TwitterAuthClient:
    """
    Handles OAuth login flow and tweet posting via Twitter API v2.
    """

    def __init__(self):
        self.oauth = None

    def authenticate(self):
        """
        Starts a PIN-based authentication session with Twitter,
        obtains access tokens, and stores them locally.
        """
        request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
        oauth = OAuth1Session(CONSUMER_KEY, client_secret=CONSUMER_SECRET)

        try:
            fetch_response = oauth.fetch_request_token(request_token_url)
        except ValueError:
            print("Invalid consumer key or secret.")
            return

        resource_owner_key = fetch_response.get("oauth_token")
        resource_owner_secret = fetch_response.get("oauth_token_secret")
        print("Got OAuth token:", resource_owner_key)

        base_authorization_url = "https://api.twitter.com/oauth/authorize"
        authorization_url = oauth.authorization_url(base_authorization_url)
        print("Please go here and authorize:", authorization_url)
        verifier = input("Paste the PIN here: ")

        access_token_url = "https://api.twitter.com/oauth/access_token"
        oauth = OAuth1Session(
            CONSUMER_KEY,
            client_secret=CONSUMER_SECRET,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
            verifier=verifier,
        )
        oauth_tokens = oauth.fetch_access_token(access_token_url)

        access_token = oauth_tokens["oauth_token"]
        access_token_secret = oauth_tokens["oauth_token_secret"]

        # Save tokens for later use
        with open(TOKEN_FILE, "w") as f:
            json.dump({
                "access_token": access_token,
                "access_token_secret": access_token_secret
            }, f)

        self.oauth = OAuth1Session(
            CONSUMER_KEY,
            client_secret=CONSUMER_SECRET,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )

        print(f"Authentication successful. Tokens saved to {TOKEN_FILE}")

    def restore_session(self):
        """
        Restores a previously authenticated session from file.
        """
        if not os.path.exists(TOKEN_FILE):
            print("No saved Twitter session found. Run authenticate() first.")
            return

        with open(TOKEN_FILE, "r") as f:
            tokens = json.load(f)

        self.oauth = OAuth1Session(
            CONSUMER_KEY,
            client_secret=CONSUMER_SECRET,
            resource_owner_key=tokens["access_token"],
            resource_owner_secret=tokens["access_token_secret"],
        )
        print("Twitter session restored.")

    def post_tweet(self, text, media_path=None):
        """
        Posts a tweet with optional image upload.

        Args:
            text (str): The body of the tweet.
            media_path (str, optional): Path to a local image file to upload.
        """
        if not self.oauth:
            raise ValueError("Twitter session not authenticated. Use authenticate() or restore_session().")

        media_id = None

        if media_path and os.path.isfile(media_path):
            try:
                with open(media_path, "rb") as media_file:
                    media_response = self.oauth.post(
                        "https://upload.twitter.com/1.1/media/upload.json",
                        files={"media": media_file}
                    )
                media_response.raise_for_status()
                media_id = media_response.json().get("media_id_string")
                print("Media uploaded. ID:", media_id)
            except Exception as e:
                print(f"Media upload failed: {e}")

        payload = {"text": text}

        if media_id:
            payload["media"] = {"media_ids": [media_id]}

        response = self.oauth.post("https://api.twitter.com/2/tweets", json=payload)

        if response.status_code != 201:
            raise Exception(f"Tweet failed: {response.status_code} {response.text}")

        print("Tweet posted successfully.")
        print(json.dumps(response.json(), indent=4, sort_keys=True))
