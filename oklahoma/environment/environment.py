from os import sep, getcwd, environ
from contextlib import suppress
from typing import overload
from ..utils import Singleton
from ..exceptions import ProfileNotFoundError
from ._load_yaml import _load_yaml_profile, Profile


class Env(metaclass=Singleton):
    _data: dict[str, str]
    _profile: str
    _cwd: str
    _loaded: bool
    _current_index: int
    _profile_obj: Profile | None

    def __init__(
        self,
        no_error: bool = True,
    ) -> None:
        self._current_index = 0
        self._profile_obj = None
        if no_error is True:
            self._profile = ""
            self._cwd = getcwd()
            self._data = dict(environ)
            self._loaded = False
        else:
            self.__reload__()

    def __reload__(self) -> None:
        if self._loaded is True:
            return
        if len(environ.get("OK_PROFILE", "").strip()) == 0:
            raise ProfileNotFoundError("OK_PROFILE not found")
        profile: str = environ["OK_PROFILE"].strip()
        cwd: str = environ.get("OK_CWD", getcwd())
        if not cwd.endswith(sep):
            cwd += sep

        self._data = dict(environ)
        self._profile = profile
        self._cwd = cwd
        del profile, cwd
        self._loaded = True
        self._profile_obj = _load_yaml_profile(
            self._cwd,
            self._profile,
        )

    def refresh(self) -> None:
        """Refresh the AWS secrets and load into the environment"""
        raise NotImplementedError()

    @property
    def profile(self) -> Profile:
        """The profile chosen"""
        if self._profile_obj is None:
            with suppress(ProfileNotFoundError):
                self.__reload__()
        if self._profile_obj is None:
            raise ProfileNotFoundError("The profile has not been loaded yet")
        return self._profile_obj

    @property
    def cwd(self) -> str:
        """Current working directory"""
        return self._cwd

    @property
    def db_uri(self) -> str:
        """The connection string"""
        raise NotImplementedError()

    def __getitem__(self, key: str) -> str:
        return self._data[key]

    def __setitem__(self, key: str, val: str) -> None:
        self._data[key] = val
        environ[key] = val

    def __delitem__(self, key: str) -> None:  # pragma: no cover
        if key in self._data:
            del self._data[key]
        if key in environ:
            del environ[key]

    def __del__(self) -> None:  # pragma: no cover
        with suppress(Exception):
            self._data.clear()

    def __contains__(self, other: object) -> bool:
        if not isinstance(other, str):
            return False
        return other in self._data

    def __iter__(self):
        self._current_index = 0
        return self

    def __next__(self) -> str:
        keys: list[str] = list(self._data.keys())
        if self._current_index < len(keys):
            key = keys[self._current_index]
            self._current_index += 1
            return key
        raise StopIteration

    @overload
    def get(self, key: str) -> str | None:
        ...  # pragma: no cover

    @overload
    def get(self, key: str, default: None) -> str | None:
        ...  # pragma: no cover

    @overload
    def get(self, key: str, default: str) -> str:
        ...  # pragma: no cover

    def get(self, key: str, default: str | None = None) -> str | None:
        """Get a value from the environment

        Args:
            key (str): The key
            default (str | None, optional): Default value. Defaults to None.

        Returns:
            str | None: The value
        """
        try:
            return self[key]
        except KeyError:
            return default
