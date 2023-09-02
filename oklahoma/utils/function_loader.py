from os import sep, getcwd
from os.path import isfile, isdir, dirname
from typing import Callable, cast
from importlib import import_module
from importlib.util import (
    spec_from_file_location,
    module_from_spec,
)
from sys import modules
from types import ModuleType
from pathlib import Path
from ..exceptions import ModuleLoadingError


def load_functions(
    *function_names: str,
    cwd: str | None = None,
    folder_name: str = "src",
) -> dict[str, Callable[..., None]]:
    """
    Load functions dynamically from modules in a specified folder.

    Args:
        *function_names: Variable-length argument list of function names to load.
        cwd: Current working directory. Defaults to None.
        folder_name: Name of the folder containing the modules. Defaults to "src".

    Returns:
        A dictionary mapping function names to the loaded functions.
    """

    # pylint: disable=unused-argument
    def _default(*args: object, **kwargs: object) -> None:
        return

    # pylint: enable=unused-argument

    _out: dict[str, Callable[..., None]] = {_key: _default for _key in function_names}
    if cwd is None:
        cwd = getcwd()
    if isfile(cwd):
        cwd = dirname(cwd)

    def _recursive_load(
        mod: object | None,
        name: str,
    ) -> None:
        if isinstance(mod, ModuleType):
            for mod_var in dir(mod):
                _recursive_load(
                    getattr(mod, mod_var, None),
                    mod_var,
                )
        elif mod is not None:
            if name in function_names and callable(mod) is True:
                _out.update({name: cast(Callable[..., None], mod)})
                return

    cwd = str(Path(cwd).absolute())
    if not cwd.endswith(sep):
        cwd += sep
    if not isdir(cwd + folder_name):
        raise ModuleLoadingError(
            f"Folder '{cwd + folder_name}' not found",
        )
        # Trying to load files dynamically
    if not isfile(cwd + folder_name + sep + "__init__.py"):
        raise ModuleLoadingError(
            "No __init__.py in folder",
        )
    # if folder_name in modules:
    #     return  # It's already loaded
    relative = str(Path(cwd + folder_name).relative_to(getcwd())).replace(sep, ".")
    import_module(relative)
    # Modules loaded correctly

    init_py = Path(cwd + folder_name + sep + "__init__.py")

    spec = spec_from_file_location(relative, init_py)
    if spec is None:  # pragma: no cover
        raise ModuleLoadingError(
            "Could not load modules",
        )
    mod: ModuleType = module_from_spec(spec)

    modules[folder_name] = mod
    if spec.loader is None:  # pragma: no cover
        raise ModuleLoadingError(
            "Could not load modules",
        )
    spec.loader.exec_module(mod)
    # Load all modules
    for mod_var in dir(mod):
        _recursive_load(
            getattr(mod, mod_var, None),
            mod_var,
        )
    return _out
