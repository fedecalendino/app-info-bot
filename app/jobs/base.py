import logging
from time import time, sleep

from slackhooks.blocks.context import Context
from slackhooks.blocks.element import MarkdownTextElement
from slackhooks.blocks.section import Section
from slackhooks.blocks.text import MarkdownText
from slackhooks.client import Message

from app import settings

MAX_RETRIES = 5

logger = logging.getLogger(__name__)


class Job:
    def __init__(self, name):
        self.name = name

    def run(self):
        try:
            sleep(1)

            logger.info("Running job '%s'", self.name)

            start = time()
            retries_left, result = self.execute_with_retries()
            end = time()

            self.notify_success(
                result=result,
                runtime=round(end - start),
                retries_left=retries_left,
            )
        except Exception as exc:
            logger.error("Error running job '%s': %s", self.name, str(exc))
            self.notify_failure(exc)

    def execute(self):
        raise NotImplementedError()

    def execute_with_retries(self, retries: int = MAX_RETRIES):
        try:
            return retries, self.execute()
        except Exception as exc:
            if retries:
                return self.execute_with_retries(retries - 1)

            raise exc

    def notify_success(self, result: str, runtime: int, retries_left: int):
        if not settings.SLACK_WEBHOOK_URL:
            return

        message = Message(
            text=f"{self.name} > finished successfully.",
            blocks=[
                Section(
                    text=MarkdownText(
                        text=f"*{self.name.upper()}* > finished successfully after {runtime} seconds. \n\n```{result}```",
                    ),
                ),
            ],
        )

        if retries_left < MAX_RETRIES:
            message.blocks.append(
                Context(
                    elements=[
                        MarkdownTextElement(text=f"{retries_left} retries left"),
                    ]
                ),
            )

        message.send(webhook_url=settings.SLACK_WEBHOOK_URL)

    def notify_failure(self, exc: Exception):
        if not settings.SLACK_WEBHOOK_URL:
            return

        Message(
            text=f"{self.name} > finished unsuccessfully.",
            blocks=[
                Section(
                    text=MarkdownText(
                        text=f"*{self.name.upper()}* > finished unsuccessfully. \n\n```{str(exc)}```",
                    ),
                ),
            ],
        ).send(
            webhook_url=settings.SLACK_WEBHOOK_URL,
        )
