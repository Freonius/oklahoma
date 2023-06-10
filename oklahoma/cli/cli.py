from os import environ
from argparse import ArgumentParser, Namespace


def cli():
    parser: ArgumentParser = ArgumentParser(
        "Oklahoma!",
        description="Program to run a FastAPI app easily",
        epilog="Oh, what a beautiful morning!",
    )
    parser.add_argument(
        "-m",
        "-module",
        default="src",
        type=str,
        dest="module",
        help="The module to load",
        required=False,
    )
    parser.add_argument(
        "-w",
        "-cwd",
        default=".",
        type=str,
        dest="cwd",
        help="The current working directory",
        required=False,
    )
    parser.add_argument(
        "-p",
        "-profile",
        type=str,
        dest="profile",
        help="The profile in oklahoma.yml",
        required=True,
    )
    parser.add_argument(
        choices=(
            "run",
            "revision",
            "migrate",
        ),
        type=str,
        default="run",
        dest="action",
        help="The action to perform",
    )
    _ns: Namespace = parser.parse_args()
    _action: object | None = getattr(_ns, "action", None)
    if _action is None or not isinstance(_action, str):
        raise TypeError("action must be str")
    _profile: object | None = getattr(_ns, "profile", None)
    if _profile is None or not isinstance(_profile, str):
        raise TypeError("profile must be str")
    _module: object | None = getattr(_ns, "module", None)
    if _module is None or not isinstance(_module, str):
        raise TypeError("module must be str")
    _cwd: object | None = getattr(_ns, "cwd", None)
    if _cwd is None or not isinstance(_cwd, str):
        raise TypeError("cwd must be str")
    del _ns, parser
    environ["OK_PROFILE"] = _profile
    environ["OK_CWD"] = _cwd
    environ["OK_MODULE"] = _module
    del _profile, _cwd, _module
    print("Oh, what a beautiful morning!")
