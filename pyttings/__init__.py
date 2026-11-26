import os
from types import ModuleType
from typing import TypeVar, cast

from pyttings.type_converter import parse_bool

from .core import Settings
from .testing import override_settings

settings = Settings(lazy_load=parse_bool(os.getenv("PYTTING_LAZY_LOAD", "False")))

_ModuleT = TypeVar("_ModuleT", bound=ModuleType)


def typed_settings(module: _ModuleT) -> _ModuleT:
    """Return the pyttings ``settings`` object typed as the given settings module.

    At runtime this returns the regular ``settings`` object (with environment
    variable overrides applied). For static type checkers and IDEs it has the
    type of ``module``, so attribute access keeps the types declared in the
    settings module and "go to definition" jumps to it.

    ``module`` is usually the one configured in ``PYTTING_SETTINGS_MODULE``,
    but it can differ (e.g. tests using their own settings module) as long as
    every setting it declares also exists in the configured module.
    """
    declared = {key for key in dir(module) if key.isupper()}
    missing = sorted(declared - settings.defaults.keys())
    if missing:
        raise ValueError(
            f"typed_settings() received module '{module.__name__}' declaring "
            f"settings missing from '{settings._settings_module}': "
            f"{', '.join(missing)}."
        )
    return cast(_ModuleT, settings)


__all__ = ["override_settings", "settings", "typed_settings"]
