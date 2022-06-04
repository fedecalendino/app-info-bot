import logging
from time import sleep
from urllib import parse

from praw.models import Submission

from appinfobot.reddit import reddit
from appinfobot.config import REDDIT_SUBREDDITS
from appinfobot.stores import SUPPORTED_STORES
from . import filters

logger = logging.getLogger(__name__)


def analyze_submission(submission: Submission):
    logger.info("Found %s app", submission.url)

    url = parse.urlsplit(submission.url)
    scraper = SUPPORTED_STORES.get(url.hostname)
    info = scraper(url.geturl())

    logger.info("Fetched information for %s from %s", info.title, info.store)

    submission.reply(body=str(info))
    logger.info("Replied to %s", submission.permalink)


def analyze_subreddit(subreddit: str) -> dict:
    logger.info("Looking for posts in /r/%s", subreddit)

    result = {
        "analyzed": [],
        "is_old": [],
        "is_self": [],
        "is_unsupported": [],
        "was_analyzed": [],
        "errors": [],
    }

    for submission in list(reddit.subreddit(subreddit).new(limit=10)):
        data = {"id": submission.id, "title": submission.title}

        if filters.is_self(submission):
            result["is_self"].append(data)
            continue

        if filters.is_old(submission):
            result["is_old"].append(data)
            continue

        if filters.is_unsupported(submission):
            result["is_unsupported"].append(data)
            continue

        if filters.was_analyzed(submission):
            result["was_analyzed"].append(data)
            continue

        try:
            analyze_submission(submission)
            sleep(1)

            result["analyzed"].append(data)
        except Exception as exc:
            data["error"] = str(exc)

            logging.error(exc, exc_info=True)
            result["errors"].append(data)

    return result


def run() -> dict:
    result = {}

    for subreddit in REDDIT_SUBREDDITS:
        result[subreddit] = analyze_subreddit(subreddit)

    return result
