import azure.functions as func

from appinfobot import jobs


def main(mytimer: func.TimerRequest) -> None:
    jobs.check()
