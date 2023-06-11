class OKException(Exception):
    pass


class ModuleLoadingError(OKException):
    ...


class ProfileNotFoundError(OKException):
    ...


class ApiLoadingError(OKException):
    pass


class SessionError(OKException):
    pass


class AlembicException(OKException):
    pass


class ShellError(OKException):
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
