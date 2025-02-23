import ast
import inspect
import os
import types
from contextlib import suppress
from typing import Any, Type, TypeVar, get_args, get_origin

from pyttings.exceptions import SettingMisconfigured

CUSTOM_CLASS_METHOD_NAME = os.getenv(
    "PYTTING_CUSTOM_CLASS_METHOD_NAME", "__pyttings_convert__"
)
CONTAINERS = (list, tuple, set, dict)
ContainerType = TypeVar("ContainerType", list, tuple, set, dict)


def is_custom_class(expected_type: type) -> bool:
    return hasattr(expected_type, CUSTOM_CLASS_METHOD_NAME) and callable(
        getattr(expected_type, CUSTOM_CLASS_METHOD_NAME)
    )


def convert_container(
    value: str, expected_type: Type[ContainerType]
) -> ContainerType | None:
    with suppress(SyntaxError, ValueError, TypeError):
        parsed_value = ast.literal_eval(value)
        return (
            expected_type(parsed_value)
            if isinstance(parsed_value, expected_type)
            else None
        )
    return None


def validate_container_types(
    value: Any, container_type: Type[ContainerType], arg_types: tuple | None
) -> bool:
    if arg_types is None:
        return True

    if container_type is dict:
        if not isinstance(value, dict):
            return False
        key_type, value_type = arg_types
        return all(
            isinstance(k, key_type) and isinstance(v, value_type)
            for k, v in value.items()
        )

    if container_type in {list, tuple, set}:
        if not isinstance(value, container_type):
            return False
        element_type = arg_types[0]
        return all(isinstance(x, element_type) for x in value)

    return False


def convert_and_validate(name: str, value: str, expected_type: type) -> Any:
    origin = get_origin(expected_type)

    if origin is types.UnionType:
        for candidate_type in get_args(expected_type):
            with suppress(SettingMisconfigured):
                return convert_and_validate(name, value, candidate_type)
        raise SettingMisconfigured(
            f"Invalid type for {name} with configured value '{value}'. "
            f"Expected one of {get_args(expected_type)}."
        )

    if origin is None:
        if is_custom_class(expected_type):
            method = getattr(expected_type, CUSTOM_CLASS_METHOD_NAME)
            params = list(inspect.signature(method).parameters.values())
            if len(params) != 1:
                raise SettingMisconfigured(
                    f"Invalid method signature for {expected_type}. "
                    f"Expected a single parameter."
                )
            param = params[0]
            if param.annotation is inspect.Parameter.empty:
                raise SettingMisconfigured(
                    f"Invalid method signature for {expected_type}. "
                    f"Expected a type hint for the parameter."
                )
            return method(convert_and_validate(name, value, param.annotation))
        elif expected_type is bool:
            return value.lower() == "true"
        elif expected_type in CONTAINERS:
            converted_value = convert_container(value, expected_type)
            if converted_value is not None:
                return converted_value
        elif expected_type is types.NoneType:
            return value
        else:
            with suppress(ValueError, TypeError):
                return expected_type(value)
    elif origin in CONTAINERS:
        converted_value = convert_container(value, origin)
        if converted_value is not None and validate_container_types(
            converted_value, origin, get_args(expected_type)
        ):
            return converted_value

    raise SettingMisconfigured(
        f"Invalid type for {name} with configured value '{value}'."
        f"\nExpected {expected_type}."
    )
