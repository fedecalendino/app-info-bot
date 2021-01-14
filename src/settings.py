import os

PORT = int(os.environ.get("PORT", 6000))
IP = "127.0.0.1" if PORT == 6000 else "0.0.0.0"

API_KEY = os.environ.get("API_KEY", "test")

DEV = os.environ.get("DEV", "https://reddit.com/user/test")
GITHUB = os.environ.get("GITHUB", "https://github.com/test/respository")

REDDIT_USERNAME = os.environ.get("REDDIT_USERNAME")
REDDIT_PASSWORD = os.environ.get("REDDIT_PASSWORD")

REDDIT_CLIENTID = os.environ.get("REDDIT_CLIENTID")
REDDIT_CLIENTSECRET = os.environ.get("REDDIT_CLIENTSECRET")
REDDIT_USERAGENT = os.environ.get("REDDIT_USERAGENT")

REDDIT_SUBREDDITS = os.environ.get("REDDIT_SUBREDDITS", "test,test2").split(",")
