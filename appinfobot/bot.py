import logging
from time import sleep
from urllib import parse

from praw.models import Submission

from appinfobot.config import REDDIT_SUBREDDITS
from appinfobot.reddit import reddit
from appinfobot.stores import SUPPORTED_STORES

logger = logging.getLogger(__name__)


def find_comment(submission: Submission):
    for comment in submission.comments:
        if comment.author == reddit.user.me():
            return comment

    return None


def analyze_submission(submission: Submission):
    url = parse.urlsplit(submission.url)

    if url.hostname not in SUPPORTED_STORES:
        logger.info("found invalid submission (%s)", submission.url)
        return

    logger.info("found valid submission (%s)", submission.url)

    scraper = SUPPORTED_STORES.get(url.hostname)
    info = scraper(url.geturl())

    logger.info("fetched information for %s (%s)", info.title, info.store)

    comment = find_comment(submission)

    if comment:
        comment.edit(body=str(info))
        logger.info("updated comment (%s)", comment.permalink)
    else:
        comment = submission.reply(body=str(info))
        logger.info("replied with comment (%s)", comment.permalink)


def analyze_subreddit(subreddit: str) -> dict:
    logger.info("looking for submissions in /r/%s", subreddit)

    result = {
        "errors": [],
    }

    for submission in list(reddit.subreddit(subreddit).new(limit=15)):
        data = {"id": submission.id, "title": submission.title}

        if submission.is_self:
            continue

        try:
            analyze_submission(submission)
        except Exception as exc:
            result["errors"].append(data)
            logging.error(exc, exc_info=True)

        sleep(1)

    return result


def run() -> dict:
    result = {}

    for subreddit in REDDIT_SUBREDDITS:
        result[subreddit] = analyze_subreddit(subreddit)

    return result
