from os.path import isfile, isdir, sep
from typing import cast
from yaml import load, SafeLoader

from ..exceptions import ProfileNotFoundError, ModuleLoadingError
from ._profile import Profile


def _load_yaml(cwd: str) -> dict[str, dict[str, dict[str, object]]]:
    if not isdir(cwd):
        raise ModuleLoadingError("Current working directory not found")
    if not cwd.endswith(sep):
        cwd += sep
    if not isfile(cwd + "oklahoma.yml"):
        raise ModuleLoadingError(f"{cwd}oklahoma.yml not found")
    with open(cwd + "oklahoma.yml", "r", encoding="utf-8") as handle:
        _data: object = load(handle, SafeLoader)
        if not isinstance(_data, dict):
            raise ModuleLoadingError("oklahoma.yml is not a dict")
        if not all(isinstance(_k, str) for _k in _data):
            raise ModuleLoadingError("Not all profiles names are strings")
        if not all(isinstance(_x, dict) for _x in _data.values()):
            raise ModuleLoadingError("Not all profiles are dictionaries")
        _data = cast(dict[str, dict], _data)
        for _v in _data.values():
            for _k in _v:
                if not isinstance(_k, str):
                    raise ModuleLoadingError("Not all keys in profiles are strings")
                if not isinstance(_v[_k], dict):
                    raise ModuleLoadingError("Not all objects in profiles are dicts")
                for _sk in _v[_k]:
                    if not isinstance(_sk, str):
                        raise ModuleLoadingError("Not all keys in objects are string")
        _data = cast(dict[str, dict[str, dict[str, object]]], _data)
        return _data


def _load_yaml_profile(cwd: str, profile: str) -> Profile:
    _yaml = _load_yaml(cwd)
    if profile not in _yaml:
        raise ProfileNotFoundError(f"Profile {profile} not found")
    return Profile(**_yaml[profile])  # type: ignore
