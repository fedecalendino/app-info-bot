from praw import Reddit

from app import config

reddit = Reddit(
    client_id=config.REDDIT_CLIENTID,
    client_secret=config.REDDIT_CLIENTSECRET,
    user_agent=config.REDDIT_USERAGENT,
    username=config.REDDIT_USERNAME,
    password=config.REDDIT_PASSWORD,
)

assert reddit.user.me().name == config.REDDIT_USERNAME
