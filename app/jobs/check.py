import logging

from app import bot
from app import settings
from .base import Job

logger = logging.getLogger(__name__)


class CheckJob(Job):
    def __init__(self):
        super().__init__("check")

    def execute(self):
        result = {}

        subreddits = settings.REDDIT_SUBREDDITS

        logger.info("analyzing: " + " ".join(subreddits))

        for subreddit in subreddits:
            result[subreddit] = bot.analyze_subreddit(subreddit)

        return " ".join(list(map(lambda sub: f"\n * {sub}", subreddits)))
