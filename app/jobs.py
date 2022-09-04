import logging
import os
from time import time, sleep

from slackhooks.blocks.section import Section
from slackhooks.blocks.text import MarkdownText
from slackhooks.client import Message

from app.config import REDDIT_SUBREDDITS
from . import bot

logger = logging.getLogger(__name__)

NAME = "check"


def check():
    result = {}

    logger.info("analyzing: " + " ".join(REDDIT_SUBREDDITS))

    for subreddit in REDDIT_SUBREDDITS:
        result[subreddit] = bot.analyze_subreddit(subreddit)


def run():
    try:
        start = time()
        logger.info("Running job '%s'", NAME)
        check()
        end = time()

        message = f"finished successfully after {round(end - start)} seconds"
    except Exception as exc:
        logger.error("Error running job '%s': %s", NAME, str(exc))
        message = f"finished unsuccessfully: {exc}"
        sleep(1)

    if not os.getenv("SLACK_WEBHOOK_URL"):
        return

    Message(
        text=f"{NAME} > {message}.",
        blocks=[
            Section(
                text=MarkdownText(
                    text=f"*{NAME.upper()}* > {message}.",
                ),
            ),
        ],
    ).send(
        webhook_url=os.getenv("SLACK_WEBHOOK_URL"),
    )
