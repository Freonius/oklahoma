from os import getcwd
from os.path import isfile, dirname
from contextlib import suppress
from fastapi.routing import APIRouter
from ...exceptions import ApiLoadingError, ModuleLoadingError
from ...utils import Singleton, load_types


class RoutesLoader(metaclass=Singleton):
    """Class to load routes for folder"""

    _modules_loaded: bool = False
    _folder_name: str
    _routes: list[APIRouter]
    _cwd: str

    def __init__(self, folder_name: str = "src", cwd: str | None = None) -> None:
        self._folder_name = folder_name
        self._routes = []
        if cwd is None:
            cwd = getcwd()
        if isfile(cwd):
            cwd = dirname(cwd)
        self._cwd = cwd

    @property
    def routes(self) -> list[APIRouter]:
        """List of loaded routes. If a routes starts\
              with '_' and __debug__ is False,
        its loading will be skipped.

        Returns:
            list[APIRouter]: The routes loaded
        """
        return self._routes

    def load_routes(self) -> None:
        """Load routes in cwd + folder_name

        Raises:
            ApiLoadingError: If it can't load the modules
        """
        if self._modules_loaded is True:
            return
        try:
            self._routes = load_types(
                APIRouter,
                instance=True,
                cwd=self._cwd,
                folder_name=self._folder_name,
            )
        except ModuleLoadingError as ex:
            raise ApiLoadingError(
                "Could not load routes",
            ) from ex

    def __del__(self) -> None:
        with suppress(Exception):
            self._routes.clear()
