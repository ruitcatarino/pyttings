import importlib
import os
from contextlib import suppress
from functools import cached_property
from typing import Any, get_type_hints

from pyttings.type_converter import convert_and_validate


class Settings:
    def __init__(self) -> None:
        """Initialize the settings manager."""
        self._settings_module: str = self._load_settings_module()
        self._env_prefix: str = os.getenv("PYTTING_ENV_PREFIX", "PYTTING_")
        self._cache: dict[str, Any] = {}

    def _load_settings_module(self) -> str:
        """Get the settings module name from environment variable."""
        settings_module: str | None = os.getenv("PYTTING_SETTINGS_MODULE")
        if settings_module is None:
            raise ValueError(
                "'PYTTING_SETTINGS_MODULE' environment variable is not set.\n"
                "Please specify a settings module."
            )
        return settings_module

    @cached_property
    def _module(self):
        """Import and cache the settings module."""
        return importlib.import_module(self._settings_module)

    @cached_property
    def _type_hints(self) -> dict[str, Any]:
        """Get type hints from the settings module."""
        with suppress(ImportError, ValueError, TypeError):
            return get_type_hints(self._module)
        return {}

    @cached_property
    def defaults(self) -> dict[str, Any]:
        """Get all uppercase attributes from the settings module as defaults."""
        return {
            key: getattr(self._module, key)
            for key in dir(self._module)
            if not key.startswith("__") and not key.endswith("__") and key.isupper()
        }

    def get_env_var(self, name: str) -> Any | None:
        """Get and convert environment variable for a setting."""
        env_var_name = f"{self._env_prefix}{name}"
        value = os.getenv(env_var_name)

        if value is None or name not in self.defaults:
            return value
        expected_type = self._type_hints.get(name, type(self.defaults[name]))
        return convert_and_validate(name, value, expected_type)

    def __getattr__(self, name: str) -> Any:
        if name not in self._cache:
            value: Any | None = self.get_env_var(name)
            if value is None:
                if name in self.defaults:
                    value = self.defaults[name]
                else:
                    raise AttributeError(
                        f"'{self.__class__.__name__}' object has no attribute '{name}'"
                    )
            self._cache[name] = value
        return self._cache[name]
