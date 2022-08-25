import logging
from time import sleep
from urllib import parse

from praw.models import Submission

from app.reddit import reddit
from app.stores import SUPPORTED_STORES

logger = logging.getLogger(__name__)


def find_comment(submission: Submission):
    for comment in submission.comments:
        try:
            if comment.author_fullname == reddit.user.me().fullname:
                return comment
        except:  # fix for deleted comments by mods.
            continue

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

    # if comment and comment.edited:
    #     logger.info(" * skipped old submission (%s)", submission.url)
    #     return

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

    for submission in list(reddit.subreddit(subreddit).new(limit=3)):
        data = {"id": submission.id, "title": submission.title}

        try:
            analyze_submission(submission)
        except Exception as exc:
            result["errors"].append(data)
            logging.error(exc, exc_info=True)

    return result
