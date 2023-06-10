from os import sep, getcwd, environ
from os.path import isfile, isdir
from yaml import load, SafeLoader
from ..utils import Singleton
from ..exceptions import ProfileNotFoundError


class Env(metaclass=Singleton):
    _data: dict[str, str]

    def __init__(self) -> None:
        if len(environ.get("OK_PROFILE", "").strip()) == 0:
            raise ProfileNotFoundError("OK_PROFILE not found")
        profile: str = environ["OK_PROFILE"].strip()
        cwd: str = environ.get("OK_CWD", getcwd())
        if not cwd.endswith(sep):
            cwd += sep
