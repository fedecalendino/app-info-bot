from urllib import parse

from praw.models import Submission

from appinfobot.config import REDDIT_USERNAME
from appinfobot.stores import SUPPORTED_STORES


def is_old(submission: Submission) -> bool:
    return submission.created_utc < 1609891200  # 2019-01-06


def is_self(submission: Submission) -> bool:
    return submission.is_self


def was_analyzed(submission: Submission) -> bool:
    for comment in submission.comments:
        author = comment.author

        if not author:
            continue

        if author.name == REDDIT_USERNAME:
            return True

    return False


def is_unsupported(submission: Submission) -> bool:
    url = parse.urlsplit(submission.url)
    return url.hostname not in SUPPORTED_STORES
