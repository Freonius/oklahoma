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
