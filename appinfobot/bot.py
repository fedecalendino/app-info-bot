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
        if comment.author_fullname == reddit.user.me().fullname:
            return comment

    return None


def analyze_submission(submission: Submission):
    if submission.is_self:
        logger.info(" * found invalid self-submission (%s)", submission.url)
        return

    url = parse.urlsplit(submission.url)

    if url.hostname not in SUPPORTED_STORES:
        logger.info(" * found invalid submission (%s)", submission.url)
        return

    comment = find_comment(submission)

    if comment.edited:
        logger.info(" * skipped old submission (%s)", submission.url)
        return

    logger.info(" * found valid submission (%s)", submission.url)

    scraper = SUPPORTED_STORES.get(url.hostname)
    info = scraper(url.geturl())

    logger.info("   - fetched information for %s (%s)", info.title, info.store)

    if comment:
        comment.edit(body=str(info))
        logger.info("   - updated comment (%s)", comment.permalink)
    else:
        comment = submission.reply(body=str(info))
        logger.info("   - replied with comment (%s)", comment.permalink)

    sleep(1)


def analyze_subreddit(subreddit: str) -> dict:
    logger.info("looking for submissions in /r/%s", subreddit)

    result = {
        "errors": [],
    }

    for submission in list(reddit.subreddit(subreddit).new(limit=5)):
        data = {"id": submission.id, "title": submission.title}

        try:
            analyze_submission(submission)
        except Exception as exc:
            result["errors"].append(data)
            logging.error(exc, exc_info=True)

    return result


def run() -> dict:
    result = {}

    logger.info("analyzing: " + " ".join(REDDIT_SUBREDDITS))

    for subreddit in REDDIT_SUBREDDITS:
        result[subreddit] = analyze_subreddit(subreddit)

    logger.info("finished...")
    return result
