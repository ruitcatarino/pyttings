import ast
import types
from contextlib import suppress
from typing import Any, get_args

from pyttings.exceptions import SettingMisconfigured


def convert_and_validate(name: str, value: str, expected_type: type) -> Any:
    if isinstance(expected_type, types.UnionType):
        for candidate_type in get_args(expected_type):
            with suppress(SettingMisconfigured):
                return convert_and_validate(name, value, candidate_type)
        raise SettingMisconfigured(
            f"Invalid type for {name} with configured value '{value}'. "
            f"Expected one of {get_args(expected_type)}."
        )

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
