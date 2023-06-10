from .environment import environ
from .api import run
from .cli import cli
from .logger import OKLogger

logger: OKLogger = OKLogger()


def main():
    """Run the Oklahoma! app"""
    cli()
    environ.__reload__()
    run()
