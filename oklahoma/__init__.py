from .environment import environ
from .api import run
from .cli import cli
from .log import OKLogger, logger


def main():
    """Run the Oklahoma! app"""
    cli()
    environ.__reload__()
    run()
