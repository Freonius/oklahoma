from ..environment import environ


def run() -> None:
    environ.__reload__()
