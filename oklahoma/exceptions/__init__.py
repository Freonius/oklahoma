class OKException(Exception):
    """Base exception for Oklahoma"""


class ModuleLoadingError(OKException):
    """Could not load the desired module"""


class ProfileNotFoundError(OKException):
    """The profile was not found"""


class ApiLoadingError(OKException):
    """Could not load FastAPI"""


class SessionError(OKException):
    """There are some problems with \
        the session"""


class AlembicException(OKException):
    """Could not launch alembic"""


class ShellError(OKException):
    """Could not execute command"""

    _cmd: str
    _err: str
    _ret: int
    _out: str

    def __init__(self, cmd: str, out: str, err: str, ret: int) -> None:
        super().__init__()
        self._cmd = cmd
        self._err = err
        self._ret = ret
        self._out = out

    def __str__(self) -> str:
        return f"""COMMAND: {self._cmd}

{'=' * 20}

RETURN CODE: {self._ret}

{'=' * 20}

STDOUT: {self._out}

{'=' * 20}

STDERR: {self._err}
"""
