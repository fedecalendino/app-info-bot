from praw import Reddit

from app import settings

reddit = Reddit(
    client_id=settings.REDDIT_CLIENTID,
    client_secret=settings.REDDIT_CLIENTSECRET,
    user_agent=settings.REDDIT_USERAGENT,
    username=settings.REDDIT_USERNAME,
    password=settings.REDDIT_PASSWORD,
)

assert reddit.user.me().name == settings.REDDIT_USERNAME
