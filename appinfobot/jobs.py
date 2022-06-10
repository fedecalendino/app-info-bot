import logging

from appinfobot.config import REDDIT_SUBREDDITS
from . import bot

logger = logging.getLogger(__name__)


def check():
    result = {}

    logger.info("analyzing: " + " ".join(REDDIT_SUBREDDITS))

    for subreddit in REDDIT_SUBREDDITS:
        result[subreddit] = bot.analyze_subreddit(subreddit)
