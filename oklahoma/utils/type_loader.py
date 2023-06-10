from os import sep, getcwd
from os.path import isfile, isdir, dirname
from typing import (
    Type,
    TypeVar,
    Literal,
    overload,
)
from importlib import import_module
from importlib.util import (
    spec_from_file_location,
    module_from_spec,
)
from sys import modules
from types import ModuleType
from inspect import isclass
from pathlib import Path
from ..exceptions import ModuleLoadingError

T = TypeVar("T")


@overload
def load_types(
    find_type: Type[T],
) -> list[T]:
    ...


@overload
def load_types(
    find_type: Type[T],
    *,
    cwd: str | None,
) -> list[T]:
    ...


@overload
def load_types(
    find_type: Type[T],
    *,
    folder_name: str,
) -> list[T]:
    ...


@overload
def load_types(
    find_type: Type[T],
    *,
    cwd: str | None,
    folder_name: str,
) -> list[T]:
    ...


@overload
def load_types(
    find_type: Type[T],
    *,
    instance: Literal[True],
) -> list[T]:
    ...


@overload
def load_types(
    find_type: Type[T],
    *,
    instance: Literal[True],
    cwd: str | None,
) -> list[T]:
    ...


@overload
def load_types(
    find_type: Type[T],
    *,
    instance: Literal[True],
    folder_name: str,
) -> list[T]:
    ...


@overload
def load_types(
    find_type: Type[T],
    *,
    instance: Literal[True],
    cwd: str | None,
    folder_name: str,
) -> list[T]:
    ...


@overload
def load_types(
    find_type: Type[T],
    *,
    instance: Literal[False],
) -> list[Type[T]]:
    ...


@overload
def load_types(
    find_type: Type[T],
    *,
    instance: Literal[False],
    cwd: str | None,
) -> list[Type[T]]:
    ...


@overload
def load_types(
    find_type: Type[T],
    *,
    instance: Literal[False],
    folder_name: str,
) -> list[Type[T]]:
    ...


@overload
def load_types(
    find_type: Type[T],
    *,
    instance: Literal[False],
    cwd: str | None,
    folder_name: str,
) -> list[Type[T]]:
    ...


def load_types(
    find_type: Type[T],
    *,
    instance: bool = True,
    cwd: str | None = None,
    folder_name: str = "src",
) -> list[Type[T]] | list[T]:
    """Load all instances or classes found in a module \
    in the current working directory

    Args:
        find_type (Type[T]): The type to look for.
        instance (bool, optional): Look for instances of \
            type T, or for classes. Defaults to True.
        cwd (str | None, optional): The current working \
            directory. Defaults to None.
        folder_name (str, optional): The name of the module\
            to load. Defaults to "src".

    Raises:
        ModuleLoadingError: If it cannot load the modules

    Returns:
        list[Type[T]] | list[T]: The classes or instances found
    """
    _types: list[Type[T]] = []
    _instances: list[T] = []
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
            if name.startswith("_") and __debug__ is False:
                return
            if (
                instance is False
                and isclass(
                    mod,
                )
                and issubclass(
                    mod,
                    find_type,
                )
            ):
                _types.append(mod)
            elif instance is True and isinstance(
                mod,
                find_type,
            ):
                _instances.append(mod)

    cwd = str(Path(cwd).absolute())
    if not cwd.endswith(sep):
        cwd += sep
    if isdir(cwd + folder_name):
        # Trying to load files dynamically
        if isfile(cwd + folder_name + sep + "__init__.py"):
            # if folder_name in modules:
            #     return  # It's already loaded
            relative = str(Path(cwd + folder_name).relative_to(getcwd())).replace(
                sep, "."
            )
            import_module(relative)
            # Modules loaded correctly

            init_py = Path(cwd + folder_name + sep + "__init__.py")

            spec = spec_from_file_location(relative, init_py)
            if spec is None:
                raise ModuleLoadingError(
                    "Could not load modules",
                )
            mod: ModuleType = module_from_spec(spec)

            modules[folder_name] = mod
            if spec.loader is None:
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
    if instance is True:
        return _instances
    return _types
