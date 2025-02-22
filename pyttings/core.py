import ast
import importlib
import os
import types
from contextlib import suppress
from functools import cached_property
from typing import Any, get_type_hints

from pyttings.type_converter import convert_and_validate


class Settings:
    def __init__(self) -> None:
        self._settings_module: str = self._get_settings_module()
        self._env_prefix: str = os.getenv("PYTTING_ENV_PREFIX", "PYTTING_")
        self._cache: dict[str, Any] = {}

    def _get_settings_module(self) -> str:
        settings_module: str | None = os.getenv("PYTTING_SETTINGS_MODULE")
        if settings_module is None:
            raise ValueError(
                "'PYTTING_SETTINGS_MODULE' environment variable is not set.\n"
                "Please specify a settings module."
            )
        return settings_module

    @cached_property
    def _module(self):
        return importlib.import_module(self._settings_module)

    @cached_property
    def _type_hints(self) -> dict[str, Any]:
        with suppress(ImportError, ValueError, TypeError):
            return get_type_hints(self._module)
        return {}

    @cached_property
    def defaults(self) -> dict[str, Any]:
        return {
            key: getattr(self._module, key)
            for key in dir(self._module)
            if not key.startswith("__") and not key.endswith("__") and key.isupper()
        }

    def get_env_var(self, name: str) -> Any | None:
        value = os.getenv(f"{self._env_prefix}{name}")

        if value is None or name not in self.defaults:
            return value

        expected_type = self._type_hints.get(name, type(self.defaults[name]))

        if expected_type is bool:
            return value.lower() == "true"
        elif expected_type in {list, tuple, set, dict}:
            with suppress(SyntaxError, ValueError, TypeError):
                parsed_value = ast.literal_eval(value)
                if isinstance(parsed_value, expected_type):
                    return expected_type(parsed_value)
        elif expected_type is types.NoneType:
            return value
        else:
            with suppress(ValueError, TypeError):
                return expected_type(value)

        raise SettingMisconfigured(
            f"Invalid type for {name} with configured value '{value}'."
            f"\nExpected {expected_type}."
        )

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
