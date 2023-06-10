from os import sep, getcwd
from os.path import isfile, isdir, dirname
from typing import Any
from importlib import import_module
from importlib.util import spec_from_file_location, module_from_spec
from contextlib import suppress
from sys import modules
from types import ModuleType
from pathlib import Path
from fastapi.routing import APIRouter
from ...exceptions import ApiLoadingException
from ...utils import Singleton


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
        """List of loaded routes. If a routes starts with '_' and __debug__ is False,
        its loading will be skipped.

        Returns:
            list[APIRouter]: The routes loaded
        """
        return self._routes

    def _recursive_load(self, mod: Any, name: str) -> None:
        if isinstance(mod, ModuleType):
            for mod_var in dir(mod):
                self._recursive_load(getattr(mod, mod_var, None), mod_var)
        elif mod is not None and isinstance(mod, APIRouter):
            if name.startswith("_") and __debug__ is False:
                return
            self._routes.append(mod)

    def load_routes(self) -> None:
        """Load modules in cwd + folder_name

        Raises:
            ApiLoadingException: If it can't load the modules
        """
        if self._modules_loaded is True:
            return
        cwd: str = self._cwd
        cwd = str(Path(cwd).absolute())
        if not cwd.endswith(sep):
            cwd += sep
        if isdir(cwd + self._folder_name):
            # Trying to load files dynamically
            if isfile(cwd + self._folder_name + sep + "__init__.py"):
                if self._folder_name in modules:
                    return  # It's already loaded
                relative = str(
                    Path(cwd + self._folder_name).relative_to(getcwd())
                ).replace(sep, ".")
                import_module(relative)
                # Modules loaded correctly
                self._modules_loaded = True

                init_py = Path(cwd + self._folder_name + sep + "__init__.py")

                spec = spec_from_file_location(relative, init_py)
                if spec is None:
                    raise ApiLoadingException("Could not load modules")
                mod: ModuleType = module_from_spec(spec)

                modules[self._folder_name] = mod
                if spec.loader is None:
                    raise ApiLoadingException("Could not load modules")
                spec.loader.exec_module(mod)
                # Load all routes
                for mod_var in dir(mod):
                    self._recursive_load(getattr(mod, mod_var, None), mod_var)

    def __del__(self) -> None:
        with suppress(Exception):
            self._routes.clear()
