class FSLException(Exception):
    pass


class ModuleLoadingError(FSLException):
    ...


class ApiLoadingError(FSLException):
    pass


class SessionError(FSLException):
    pass


class AlembicException(FSLException):
    pass
