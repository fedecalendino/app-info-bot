import azure.functions as func

from app import jobs


def main(mytimer: func.TimerRequest) -> None:
    jobs.check()
