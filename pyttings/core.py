import importlib
import os
from functools import cached_property
from typing import Any


class Settings:
    def __init__(self) -> None:
        self._settings_module: str = self._get_settings_module()
        self._env_prefix: str = os.getenv("PYTTING_ENV_PREFIX", "PYTTING_")
        self._cache: dict[str, Any] = {}

    @cached_property
    def defaults(self) -> dict[str, Any]:
        module = importlib.import_module(self._settings_module)
        return {
            key: getattr(module, key)
            for key in dir(module)
            if not key.startswith("__") and not key.endswith("__") and key.isupper()
        }

    def _get_settings_module(self) -> str:
        settings_module: str | None = os.getenv("PYTTING_SETTINGS_MODULE")
        if settings_module is None:
            raise ValueError(
                "PYTTING_SETTINGS_MODULE environment variable is not set. "
                "Please specify a settings module."
            )
        return settings_module

    def _get_env_var(self, name: str) -> Any | None:
        value = os.getenv(f"{self._env_prefix}{name}")
        if value is None:
            return None

        if name not in self.defaults:
            return value

        value_type = type(self.defaults[name])

        if value_type is bool:
            return value.lower() == "true"

        if value_type is type(None):
            value_type = str

        return value_type(value)

    def __getattr__(self, name: str) -> Any:
        if name not in self._cache:
            value: Any | None = self._get_env_var(name)
            if value is None:
                if name in self.defaults:
                    value = self.defaults[name]
                else:
                    raise AttributeError(
                        f"'{self.__class__.__name__}' object has no attribute '{name}'"
                    )
            self._cache[name] = value
        return self._cache[name]
