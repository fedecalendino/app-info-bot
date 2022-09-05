import azure.functions as func

from app.jobs.check import CheckJob


def main(mytimer: func.TimerRequest) -> None:
    CheckJob().run()
