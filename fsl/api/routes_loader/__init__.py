from os import sep, getcwd
from os.path import isfile, isdir, dirname
from importlib import import_module
from importlib.util import spec_from_file_location, module_from_spec
from sys import modules
from types import ModuleType
from pathlib import Path
from fastapi.routing import APIRouter

class RoutesLoader:
    _modules_loaded: bool = False
    _folder_name: str
    _routes: list[APIRouter]
    _cwd: str

    def __init__(self, folder_name: str = 'src', cwd: str | None = None) -> None:
        self._folder_name = folder_name
        self._routes = []
        if cwd is None:
            cwd = getcwd()
        if isfile(cwd):
            cwd = dirname(cwd)
        self._cwd = cwd

    def load_routes(self) -> None:
        """Load modules in cwd + folder_name"""
        if self._modules_loaded is True:
            return
        cwd: str = self._cwd
        cwd = str(Path(cwd).absolute())
        if not cwd.endswith(sep):
            cwd += sep
        if isdir(cwd + self._folder_name):
            # Trying to load files dynamically
            if isfile(cwd + self._folder_name + sep + '__init__.py'):
                if self._folder_name in modules:
                    return  # It's already loaded
                relative = str(
                    Path(cwd + self._folder_name).relative_to(getcwd())).replace(sep, '.')
                import_module(relative)
                # Modules loaded correctly
                self._modules_loaded = True

                fn = Path(cwd + self._folder_name +
                          sep + '__init__.py')

                spec = spec_from_file_location(relative, fn)
                if spec is None:
                    raise Exception('Could not load modules')
                mod: ModuleType = module_from_spec(spec)

                modules[self._folder_name] = mod
                if spec.loader is None:
                    raise Exception('Could not load modules')
                spec.loader.exec_module(mod)
                # Load all routes
                for mod_var in dir(mod):
                    if mod_var.lower() in ('routes', 'api') and isinstance(getattr(mod, mod_var, None), ModuleType):
                        for submod_var in dir(getattr(mod, mod_var, None)):
                            if isinstance(getattr(getattr(mod, mod_var, None), submod_var, None), ModuleType):
                                for subsub in dir(getattr(getattr(mod, mod_var, None), submod_var, None)):
                                    if ((_route := getattr(getattr(getattr(mod, mod_var, None), submod_var, None), subsub, None)) is not None and isinstance(_route, APIRouter)):
                                        if subsub.startswith('_') and __debug__ is False:
                                            continue
                                        self._routes.append(_route)
