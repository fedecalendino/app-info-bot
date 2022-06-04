import json

import azure.functions as func

from appinfobot import bot


def main(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(json.dumps(bot.run()))
