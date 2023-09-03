from os import environ
from sys import path
from pathlib import Path
from typing import cast
from types import ModuleType
from inspect import stack, getmodule


def setup_tests(
    cwd: str | None = None,
    module: str = "src",
    profile: str = "test",
) -> None:
    """
    Sets up the tests by configuring the working directory, module, and profile.

    Args:
        cwd (str | None, optional): The current working directory. Defaults to None.
        module (str, optional): The name of the module. Defaults to "src".
        profile (str, optional): The name of the profile. Defaults to "test".

    Returns:
        None: This function does not return anything.
    """
    if cwd is None:
        all_frames = stack()
        _mod: ModuleType | None = None
        for frame in all_frames:
            _mod = getmodule(frame[0])
            if (
                module is not None
                and (_tmp_file := cast(ModuleType, _mod).__file__) is not None
                and "test" in _tmp_file
            ):
                break
        if _mod is None:  # pragma: no cover
            cwd = "."
        else:
            filename = _mod.__file__
            if filename is None:  # pragma: no cover
                cwd = "."
            else:
                cwd = str(Path(filename).parent.parent.absolute())
    environ["OK_PROFILE"] = profile
    environ["OK_CWD"] = cwd
    environ["OK_MODULE"] = module
    path.append(str(Path(cwd).absolute()))
