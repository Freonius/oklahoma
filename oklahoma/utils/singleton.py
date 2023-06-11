from typing import Type


class Singleton(type):
    """Singleton metaclass.

    Usage:
    >>> class MyClass(metaclass=Singleton):
    >>>     pass
    """

    _instances: dict[Type, object] = {}

    def __call__(cls, *args: object, **kwargs: object) -> object:
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
