from typing import Callable
from inspect import signature, Signature


def accepts_kwargs(fun: Callable[..., None]) -> bool:
    """
    Generates a function comment for the given function body.

    Parameters:
        fun (Callable[..., None]): The function to generate a comment for.

    Returns:
        bool: True if the function accepts **kwargs, False otherwise.
    """
    sig: Signature = signature(fun)
    params = sig.parameters.values()
    return any([True for p in params if p.kind == p.VAR_KEYWORD])
