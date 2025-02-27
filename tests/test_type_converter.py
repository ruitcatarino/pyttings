import os
import types
from decimal import Decimal
from importlib import reload
from typing import Dict, List, Set, Tuple, Union

import pytest

from pyttings.exceptions import SettingMisconfigured
from pyttings.type_converter import (
    convert_and_validate,
    convert_container,
    is_custom_class,
    validate_container_types,
)


class SimpleCustomClass:
    def __init__(self, value):
        self.value = value

    @classmethod
    def __pyttings_convert__(cls, value: List[int]):
        return cls(value)

    def __eq__(self, other):
        if not isinstance(other, SimpleCustomClass):
            return False
        return self.value == other.value


class InvalidCustomClass:
    @classmethod
    def __pyttings_convert__(cls):
        # Missing parameter
        return cls()


class UntypedCustomClass:
    @classmethod
    def __pyttings_convert__(cls, value):
        # Missing type hint
        return cls(value)

    def __init__(self, value):
        self.value = value


# Test is_custom_class function
def test_is_custom_class():
    assert is_custom_class(SimpleCustomClass) is True
    assert is_custom_class(int) is False
    assert is_custom_class(str) is False

    # Test with different method name
    original_method_name = os.environ.get("PYTTING_CUSTOM_CLASS_METHOD_NAME")
    try:
        os.environ["PYTTING_CUSTOM_CLASS_METHOD_NAME"] = "custom_convert"

        class CustomMethodClass:
            @classmethod
            def custom_convert(cls, value: int):
                return cls(value)

            def __init__(self, value):
                self.value = value

        import pyttings.type_converter

        reload(pyttings.type_converter)

        assert pyttings.type_converter.is_custom_class(CustomMethodClass) is True
        assert pyttings.type_converter.is_custom_class(SimpleCustomClass) is False
    finally:
        if original_method_name is None:
            del os.environ["PYTTING_CUSTOM_CLASS_METHOD_NAME"]
        else:
            os.environ["PYTTING_CUSTOM_CLASS_METHOD_NAME"] = original_method_name
        reload(pyttings.type_converter)


# Test convert_container function
def test_convert_container_list():
    # Valid list
    assert convert_container("[1, 2, 3]", list) == [1, 2, 3]
    # Valid list with strings
    assert convert_container('["a", "b", "c"]', list) == ["a", "b", "c"]
    # Invalid syntax
    assert convert_container("[1, 2, 3", list) is None
    # Wrong type
    assert convert_container('{"a": 1}', list) is None


def test_convert_container_tuple():
    # Valid tuple
    assert convert_container("(1, 2, 3)", tuple) == (1, 2, 3)
    # Valid tuple with strings
    assert convert_container('("a", "b", "c")', tuple) == ("a", "b", "c")
    # Invalid syntax
    assert convert_container("(1, 2, 3", tuple) is None
    # Wrong type
    assert convert_container("[1, 2, 3]", tuple) is None


def test_convert_container_set():
    # Valid set
    assert convert_container("{1, 2, 3}", set) == {1, 2, 3}
    # Valid set with strings
    assert convert_container('{"a", "b", "c"}', set) == {"a", "b", "c"}
    # Invalid syntax
    assert convert_container("{1, 2, 3", set) is None
    # Wrong type
    assert convert_container("[1, 2, 3]", set) is None


def test_convert_container_dict():
    # Valid dict
    assert convert_container('{"a": 1, "b": 2}', dict) == {"a": 1, "b": 2}
    # Valid dict with nested structures
    assert convert_container('{"a": [1, 2], "b": {"c": 3}}', dict) == {
        "a": [1, 2],
        "b": {"c": 3},
    }
    # Invalid syntax
    assert convert_container('{"a": 1, "b": 2', dict) is None
    # Wrong type
    assert convert_container("[1, 2, 3]", dict) is None


# Test validate_container_types function
def test_validate_container_types_list():
    # Valid homogeneous list
    assert validate_container_types([1, 2, 3], list, (int,)) is True
    # Valid mixed list (when type checking is not enforced)
    assert validate_container_types([1, "a", 3.0], list, None) is True
    # Invalid type
    assert validate_container_types([1, "a", 3], list, (int,)) is False
    # Not a list
    assert validate_container_types({1, 2, 3}, list, (int,)) is False


def test_validate_container_types_tuple():
    # Valid homogeneous tuple
    assert validate_container_types((1, 2, 3), tuple, (int,)) is True
    # Valid mixed tuple (when type checking is not enforced)
    assert validate_container_types((1, "a", 3.0), tuple, None) is True
    # Invalid type
    assert validate_container_types((1, "a", 3), tuple, (int,)) is False
    # Not a tuple
    assert validate_container_types([1, 2, 3], tuple, (int,)) is False


def test_validate_container_types_set():
    # Valid homogeneous set
    assert validate_container_types({1, 2, 3}, set, (int,)) is True
    # Valid mixed set (when type checking is not enforced)
    assert validate_container_types({1, "a", 3.0}, set, None) is True
    # Invalid type
    assert validate_container_types({1, "a", 3}, set, (int,)) is False
    # Not a set
    assert validate_container_types([1, 2, 3], set, (int,)) is False


def test_validate_container_types_dict():
    # Valid homogeneous dict
    assert validate_container_types({"a": 1, "b": 2}, dict, (str, int)) is True
    # Valid mixed dict (when type checking is not enforced)
    assert validate_container_types({"a": 1, 2: "b"}, dict, None) is True
    # Invalid key type
    assert validate_container_types({1: "a", 2: "b"}, dict, (str, str)) is False
    # Invalid value type
    assert validate_container_types({"a": 1, "b": 2}, dict, (str, str)) is False
    # Not a dict
    assert validate_container_types([1, 2, 3], dict, (str, int)) is False


# Test convert_and_validate function
def test_convert_and_validate_simple_types():
    # Integer
    assert convert_and_validate("TEST_INT", "42", int) == 42
    # String
    assert convert_and_validate("TEST_STR", "hello", str) == "hello"
    # Boolean - true
    assert convert_and_validate("TEST_BOOL", "true", bool) is True
    # Boolean - false
    assert convert_and_validate("TEST_BOOL", "false", bool) is False
    # Boolean - case insensitive
    assert convert_and_validate("TEST_BOOL", "TRUE", bool) is True
    # Float
    assert convert_and_validate("TEST_FLOAT", "3.14", float) == 3.14
    # Decimal
    assert convert_and_validate("TEST_DECIMAL", "3.14", Decimal) == Decimal("3.14")
    # None - returns the string value
    assert convert_and_validate("TEST_NONE", "null", types.NoneType) == "null"


def test_convert_and_validate_failures():
    # Invalid int
    with pytest.raises(
        SettingMisconfigured,
        match="Invalid type for TEST_INT with configured value 'abc'",
    ):
        convert_and_validate("TEST_INT", "abc", int)

    # Invalid float
    with pytest.raises(
        SettingMisconfigured,
        match="Invalid type for TEST_FLOAT with configured value 'xyz'",
    ):
        convert_and_validate("TEST_FLOAT", "xyz", float)


def test_convert_and_validate_containers():
    # List
    assert convert_and_validate("TEST_LIST", "[1, 2, 3]", list) == [1, 2, 3]
    # Tuple
    assert convert_and_validate("TEST_TUPLE", "(1, 2, 3)", tuple) == (1, 2, 3)
    # Set
    assert convert_and_validate("TEST_SET", "{1, 2, 3}", set) == {1, 2, 3}
    # Dict
    assert convert_and_validate("TEST_DICT", '{"a": 1, "b": 2}', dict) == {
        "a": 1,
        "b": 2,
    }


def test_convert_and_validate_typed_containers():
    # List[int]
    list_int_type = List[int]
    assert convert_and_validate("TEST_LIST", "[1, 2, 3]", list_int_type) == [1, 2, 3]

    # List[str]
    list_str_type = List[str]
    assert convert_and_validate("TEST_LIST", '["a", "b", "c"]', list_str_type) == [
        "a",
        "b",
        "c",
    ]

    # Invalid list[int]
    with pytest.raises(
        SettingMisconfigured, match="Invalid type for TEST_LIST with configured value"
    ):
        convert_and_validate("TEST_LIST", '["a", "b", "c"]', list_int_type)

    # Tuple[int, ...]
    tuple_int_type = Tuple[int, ...]
    assert convert_and_validate("TEST_TUPLE", "(1, 2, 3)", tuple_int_type) == (1, 2, 3)

    # Set[str]
    set_str_type = Set[str]
    assert convert_and_validate("TEST_SET", '{"a", "b", "c"}', set_str_type) == {
        "a",
        "b",
        "c",
    }

    # Dict[str, int]
    dict_str_int_type = Dict[str, int]
    assert convert_and_validate("TEST_DICT", '{"a": 1, "b": 2}', dict_str_int_type) == {
        "a": 1,
        "b": 2,
    }

    # Invalid Dict[str, int]
    with pytest.raises(
        SettingMisconfigured, match="Invalid type for TEST_DICT with configured value"
    ):
        convert_and_validate("TEST_DICT", '{"a": "1", "b": "2"}', dict_str_int_type)


def test_convert_and_validate_union_types():
    # Union[int, str]
    union_type = Union[int, str]
    assert convert_and_validate("TEST_UNION", "42", union_type) == 42
    assert convert_and_validate("TEST_UNION", "hello", union_type) == "hello"

    # Union with container types
    union_container_type = Union[List[int], Dict[str, int]]
    assert convert_and_validate("TEST_UNION", "[1, 2, 3]", union_container_type) == [
        1,
        2,
        3,
    ]
    assert convert_and_validate(
        "TEST_UNION", '{"a": 1, "b": 2}', union_container_type
    ) == {"a": 1, "b": 2}

    # Invalid Union
    with pytest.raises(
        SettingMisconfigured, match="Invalid type for TEST_UNION with configured value"
    ):
        convert_and_validate("TEST_UNION", "xyz", Union[int, float])


def test_convert_and_validate_custom_class():
    # Valid custom class
    assert convert_and_validate(
        "TEST_CUSTOM", "[1, 2, 3]", SimpleCustomClass
    ) == SimpleCustomClass([1, 2, 3])

    # Invalid parameter for custom class
    with pytest.raises(
        SettingMisconfigured, match="Invalid type for TEST_CUSTOM with configured value"
    ):
        convert_and_validate("TEST_CUSTOM", '["a", "b", "c"]', SimpleCustomClass)

    # Custom class with invalid method signature
    with pytest.raises(
        SettingMisconfigured,
        match="Invalid method signature for.*Expected a single parameter",
    ):
        convert_and_validate("TEST_CUSTOM", "[1, 2, 3]", InvalidCustomClass)

    # Custom class with missing type hint
    with pytest.raises(
        SettingMisconfigured, match="Invalid method signature for.*Expected a type hint"
    ):
        convert_and_validate("TEST_CUSTOM", "[1, 2, 3]", UntypedCustomClass)
