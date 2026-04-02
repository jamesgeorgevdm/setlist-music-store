"""
twitter_auth.py

Handles OAuth1-based authentication with the Twitter API and provides
a client for posting tweets (with optional media upload) from the app.

Saves and restores session tokens locally or via environment variables.
"""

import os
import json
from requests_oauthlib import OAuth1Session

# Twitter API credentials
CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")

# Token file location (for local development)
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "twitter_tokens.json")


class TwitterAuthClient:
    """
    Handles OAuth login flow and tweet posting via Twitter API v2.
    """

    def __init__(self):
        self.oauth = None

    def authenticate(self):
        """
        Starts a PIN-based authentication session with Twitter.
        NOTE: This should only be run locally in your terminal, not on Render.
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

        # Save tokens locally
        with open(TOKEN_FILE, "w") as f:
            json.dump({
                "access_token": access_token,
                "access_token_secret": access_token_secret
            }, f)

        print(f"Authentication successful. Tokens saved to {TOKEN_FILE}")
        print("--- RENDER TIP ---")
        print(f"Add TWITTER_ACCESS_TOKEN: {access_token}")
        print(f"Add TWITTER_ACCESS_TOKEN_SECRET: {access_token_secret}")
        print("to your Render Environment Variables to keep this working in the cloud.")

    def restore_session(self):
        """
        Restores a previously authenticated session.
        Prioritizes Environment Variables (Render) over local JSON files.
        """
        # 1. Try Environment Variables first (Best for Production/Render)
        access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

        if access_token and access_token_secret:
            self.oauth = OAuth1Session(
                CONSUMER_KEY,
                client_secret=CONSUMER_SECRET,
                resource_owner_key=access_token,
                resource_owner_secret=access_token_secret,
            )
            return

        # 2. Fallback to local file (Best for Local Dev)
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "r") as f:
                tokens = json.load(f)
            
            self.oauth = OAuth1Session(
                CONSUMER_KEY,
                client_secret=CONSUMER_SECRET,
                resource_owner_key=tokens["access_token"],
                resource_owner_secret=tokens["access_token_secret"],
            )
        else:
            raise ValueError("No Twitter tokens found in Environment or JSON file.")

    def post_tweet(self, text, media_path=None):
        """
        Posts a tweet with optional image upload.
        """
        if not self.oauth:
            self.restore_session()

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
            except Exception as e:
                print(f"Media upload failed: {e}")

        payload = {"text": text}
        if media_id:
            payload["media"] = {"media_ids": [media_id]}

        response = self.oauth.post("https://api.twitter.com/2/tweets", json=payload)

        if response.status_code not in [200, 201]:
            raise Exception(f"Tweet failed: {response.status_code} {response.text}")

def post_tweet(message):
    """
    Standard function wrapper to allow Django views to call
    post_tweet(message) directly without managing the class.
    """
    client = TwitterAuthClient()
    client.post_tweet(message)