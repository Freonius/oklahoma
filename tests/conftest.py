from os import environ
from sys import path
from pathlib import Path


def setup_tests_local(
    module: str = "src",
    profile: str = "test",
    cwd: str = ".",
) -> None:
    environ["OK_PROFILE"] = profile
    environ["OK_CWD"] = cwd
    environ["OK_MODULE"] = module
    path.append(str(Path(cwd).absolute()))


setup_tests_local()
from oklahoma.fixtures import setup_tests, client

setup_tests()
