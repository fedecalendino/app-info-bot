import os


GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "test/respository")

REDDIT_DEV_USERNAME = os.environ.get("REDDIT_DEV_USERNAME", "test")

REDDIT_USERNAME = os.environ.get("REDDIT_USERNAME")
REDDIT_PASSWORD = os.environ.get("REDDIT_PASSWORD")

REDDIT_CLIENTID = os.environ.get("REDDIT_CLIENTID")
REDDIT_CLIENTSECRET = os.environ.get("REDDIT_CLIENTSECRET")
REDDIT_USERAGENT = os.environ.get("REDDIT_USERAGENT")

REDDIT_SUBREDDITS = os.environ.get("REDDIT_SUBREDDITS", "test,test2").split(",")


URL_REDDIT_DEV = f"https://reddit.com/user/{REDDIT_DEV_USERNAME}"
URL_GITHUB_REPOSITORY = f"https://github.com/{GITHUB_REPOSITORY}"