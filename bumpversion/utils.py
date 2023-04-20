"""Various utility functions."""
from importlib import import_module
from typing import Any


def import_path(path: str) -> Any:
    """Import a dotted path and return the attribute or class defined.

    Raises:
        ImportError: If the import fails.
    """
    try:
        module_name, class_name = path.rsplit(".", 1)
    except ValueError as error:
        raise ImportError("'{}' is not a valid dotted path.".format(path)) from error

    try:
        module = import_module(module_name)
    except ValueError as error:
        raise ImportError(str(error)) from error

    try:
        return getattr(module, class_name)
    except AttributeError as error:
        raise ImportError(
            "'{}' does not have a class or attribute '{}'.".format(module_name, class_name)
        ) from error


def load_instance(_path: str, /, **kwargs: Any) -> Any:
    """Return instance of class specified by a dotted path and keyword arguments."""
    cls = import_path(_path)
    return cls(**kwargs)
