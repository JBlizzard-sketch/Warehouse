import tweepy
import os
from .social_agent import SocialAgent # Import shared social agent

class MultiPlatformAgent:
def init(self):
self.social_agent = SocialAgent()
self.auth = tweepy.OAuthHandler(os.getenv("TWITTER_API_KEY"), os.getenv("TWITTER_API_SECRET"))
self.auth.set_access_token(os.getenv("TWITTER_ACCESS_TOKEN"), os.getenv("TWITTER_ACCESS_TOKEN_SECRET"))
self.twitter_api = tweepy.API(self.auth)

def tweet(self, content):
    try:
        self.twitter_api.update_status(content)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def post_instagram(self, content):
    try:
        # Instagram stub
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def post_linkedin(self, content):
    try:
        # LinkedIn stub
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
