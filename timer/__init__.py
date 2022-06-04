import datetime
import logging

import azure.functions as func
from appinfobot import bot


def main(mytimer: func.TimerRequest) -> None:
    bot.run()
