import ast
import inspect
import os
import types
from contextlib import suppress
from typing import Any, Type, TypeVar, Union, get_args, get_origin

from pyttings.exceptions import SettingMisconfigured

CollectionT = TypeVar("CollectionT", list, tuple, set, dict)
CONTAINER_TYPES = {list, tuple, set, dict}
UNION_TYPES = {types.UnionType, Union}

CUSTOM_CLASS_METHOD_NAME = os.getenv(
    "PYTTING_CUSTOM_CLASS_METHOD_NAME", "__pyttings_convert__"
)


def is_custom_class(expected_type: type) -> bool:
    """Check if a type has a custom conversion method."""
    return hasattr(expected_type, CUSTOM_CLASS_METHOD_NAME) and callable(
        getattr(expected_type, CUSTOM_CLASS_METHOD_NAME)
    )


def convert_container(
    value: str, expected_type: Type[CollectionT]
) -> CollectionT | None:
    """Try to convert a string to a container type using ast.literal_eval."""
    with suppress(SyntaxError, ValueError, TypeError):
        parsed_value = ast.literal_eval(value)
        return (
            expected_type(parsed_value)
            if isinstance(parsed_value, expected_type)
            else None
        )
    return None


def validate_container_types(
    value: Any, container_type: Type[CollectionT], arg_types: tuple | None
) -> bool:
    """Validate that container elements match their expected types."""
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


def handle_union_type(name: str, value: str, union_type: type) -> Any:
    """Try to convert the value to any of the types in the union."""
    for candidate_type in get_args(union_type):
        with suppress(SettingMisconfigured):
            return convert_and_validate(name, value, candidate_type)

    raise SettingMisconfigured(
        f"Invalid type for {name} with configured value '{value}'. "
        f"Expected one of {get_args(union_type)}."
    )


def handle_custom_class(name: str, value: str, cls_type: type) -> Any:
    """Handle conversion for custom classes with conversion methods."""
    method = getattr(cls_type, CUSTOM_CLASS_METHOD_NAME)
    params = list(inspect.signature(method).parameters.values())

    if len(params) != 1:
        raise SettingMisconfigured(
            f"Invalid method signature for {cls_type}. Expected a single parameter."
        )

    param = params[0]
    if param.annotation is inspect.Parameter.empty:
        raise SettingMisconfigured(
            f"Invalid method signature for {cls_type}. "
            f"Expected a type hint for the parameter."
        )

    converted_param = convert_and_validate(name, value, param.annotation)
    return method(converted_param)


def handle_simple_type(name: str, value: str, expected_type: type) -> Any:
    """Handle conversion for simple, non-generic types."""
    if expected_type is bool:
        return value.lower() == "true"
    elif expected_type is types.NoneType:
        return value
    elif expected_type in CONTAINER_TYPES:
        converted_value = convert_container(value, expected_type)
        if converted_value is not None:
            return converted_value
    else:
        with suppress(ValueError, TypeError):
            return expected_type(value)

    raise SettingMisconfigured(
        f"Invalid type for {name} with configured value '{value}'."
        f"\nExpected {expected_type}."
    )


def handle_generic_container(
    name: str, value: str, origin: type, expected_type: type
) -> Any:
    """Handle conversion for generic container types."""
    converted_value = convert_container(value, origin)
    if converted_value is not None and validate_container_types(
        converted_value, origin, get_args(expected_type)
    ):
        return converted_value

    raise SettingMisconfigured(
        f"Invalid type for {name} with configured value '{value}'."
        f"\nExpected {expected_type}."
    )


def convert_and_validate(name: str, value: str, expected_type: type) -> Any:
    origin = get_origin(expected_type)

    if origin in UNION_TYPES:
        return handle_union_type(name, value, expected_type)

    if origin is None:
        if is_custom_class(expected_type):
            return handle_custom_class(name, value, expected_type)

        return handle_simple_type(name, value, expected_type)
    elif origin in CONTAINER_TYPES:
        return handle_generic_container(name, value, origin, expected_type)

    raise SettingMisconfigured(
        f"Invalid type for {name} with configured value '{value}'."
        f"\nExpected {expected_type}."
    )
