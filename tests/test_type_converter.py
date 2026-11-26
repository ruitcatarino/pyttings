import os
import types
from decimal import Decimal
from importlib import reload
from typing import Any, Dict, List, Literal, Optional, Set, Tuple, Union

import pytest

from pyttings.exceptions import SettingMisconfigured
from pyttings.type_converter import (
    convert_and_validate,
    convert_container,
    is_custom_class,
    parse_bool,
    validate_container_types,
)
from tests.postponed_annotations import PostponedListOfInts
from tests.utils import (
    InvalidCustomClass,
    QuotedAnnotationCustomClass,
    SimpleCustomClass,
    UntypedCustomClass,
)


# Test is_custom_class function
def test_is_custom_class():
    assert is_custom_class(SimpleCustomClass) is True
    assert is_custom_class(int) is False
    assert is_custom_class(str) is False

    # Test with different method name
    try:
        os.environ["PYTTING_CUSTOM_CLASS_METHOD_NAME"] = "custom_convert"

        class CustomMethodClass:
            @classmethod
            def custom_convert(cls, value: int): ...

            def __init__(self, value): ...

        import pyttings.type_converter

        reload(pyttings.type_converter)

        assert pyttings.type_converter.is_custom_class(CustomMethodClass) is True
        assert pyttings.type_converter.is_custom_class(SimpleCustomClass) is False
    finally:
        del os.environ["PYTTING_CUSTOM_CLASS_METHOD_NAME"]
        reload(pyttings.type_converter)


# Test parse_bool function
def test_parse_bool():
    assert parse_bool("true") is True
    assert parse_bool("false") is False
    assert parse_bool("True") is True
    assert parse_bool("False") is False
    assert parse_bool("TRUE") is True
    assert parse_bool("FALSE") is False
    assert parse_bool("1") is True
    assert parse_bool("0") is False
    assert parse_bool("yes") is True
    assert parse_bool("no") is False
    assert parse_bool("y") is True
    assert parse_bool("n") is False
    assert parse_bool("on") is True
    assert parse_bool("off") is False
    with pytest.raises(ValueError, match="Cannot parse 'abc' as boolean"):
        parse_bool("abc")


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
    # Valid mixed tuple (when type checking is not enforced)
    assert validate_container_types((1, "a", 3.0), tuple, None) is True
    # tuple[int] is exactly one element
    assert validate_container_types((1,), tuple, (int,)) is True
    assert validate_container_types((1, 2, 3), tuple, (int,)) is False
    assert validate_container_types((1, "a", 3), tuple, (int,)) is False
    # Not a tuple
    assert validate_container_types([1], tuple, (int,)) is False


def test_validate_container_types_fixed_length_tuple():
    # Each position is checked against its own type and the length must match
    assert validate_container_types((1, "a"), tuple, (int, str)) is True
    assert validate_container_types(("a", 1), tuple, (int, str)) is False
    assert validate_container_types((1,), tuple, (int, str)) is False
    # tuple[()] only accepts the empty tuple
    assert validate_container_types((), tuple, ()) is True
    assert validate_container_types((1,), tuple, ()) is False


def test_validate_container_types_variadic_tuple():
    # tuple[int, ...] accepts any number of ints
    assert validate_container_types((), tuple, (int, Ellipsis)) is True
    assert validate_container_types((1, 2, 3), tuple, (int, Ellipsis)) is True
    assert validate_container_types((1, "a"), tuple, (int, Ellipsis)) is False
    # Ellipsis is only valid as tuple[T, ...]
    assert validate_container_types((1, 1), tuple, (int, str, Ellipsis)) is False
    assert validate_container_types((1, 1), tuple, (Ellipsis, int)) is False


def test_convert_and_validate_tuples():
    assert convert_and_validate("T", '(1, "b")', Tuple[int, str]) == (1, "b")
    assert convert_and_validate("T", "(1, 2, 3)", Tuple[int, ...]) == (1, 2, 3)
    with pytest.raises(SettingMisconfigured):
        convert_and_validate("T", "(1, 2)", Tuple[int, str])
    assert convert_and_validate("T", "(1,)", Tuple[int]) == (1,)
    with pytest.raises(SettingMisconfigured):
        convert_and_validate("T", "(1, 2)", Tuple[int])
    with pytest.raises(SettingMisconfigured):
        convert_and_validate("T", "(1, 1)", Tuple[int, str, ...])


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


def test_validate_container_types_invalid():
    # Invalid container type
    assert validate_container_types([1, 2, 3], int, (int,)) is False


def test_validate_container_types_no_args():
    # Invalid container type
    assert validate_container_types([1, 2, 3], int, None) is True


def test_validate_container_types_nested():
    # Nested lists are validated recursively
    assert validate_container_types([[1, 2], [3]], list, (list[int],)) is True
    assert validate_container_types([[1, 2], [3, "a"]], list, (list[int],)) is False
    # Nested dict values are validated recursively
    assert validate_container_types({"a": [1, 2]}, dict, (str, list[int])) is True
    assert validate_container_types({"a": [1, "b"]}, dict, (str, list[int])) is False
    # Nested dict keys are validated recursively
    assert validate_container_types({("a",): 1}, dict, (tuple[str], int)) is True
    assert validate_container_types({("a", 1): 1}, dict, (tuple[str], int)) is False


def test_validate_container_types_any_and_none():
    # Any accepts every element
    assert validate_container_types([1, "a", None], list, (Any,)) is True
    # None only accepts None elements
    assert validate_container_types([None, None], list, (None,)) is True
    assert validate_container_types([None, 1], list, (None,)) is False


def test_validate_container_types_union_with_literal():
    union_type = Union[Literal["a", "b"], int]
    assert validate_container_types([1, "a"], list, (union_type,)) is True
    assert validate_container_types(["b"], list, (union_type,)) is True
    assert validate_container_types(["c"], list, (union_type,)) is False
    assert validate_container_types([1.0], list, (union_type,)) is False


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

    # Invalid decimal (raises decimal.InvalidOperation, an ArithmeticError)
    with pytest.raises(SettingMisconfigured):
        convert_and_validate("TEST_DECIMAL", "abc", Decimal)


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


def test_convert_and_validate_nested_containers():
    assert convert_and_validate("TEST_LIST", "[[1, 2], [3]]", list[list[int]]) == [
        [1, 2],
        [3],
    ]
    with pytest.raises(SettingMisconfigured, match="Invalid type for TEST_LIST"):
        convert_and_validate("TEST_LIST", "[[1, 2], [3, 'a']]", list[list[int]])

    assert convert_and_validate("TEST_DICT", '{"a": [1, 2]}', dict[str, list[int]]) == {
        "a": [1, 2]
    }
    with pytest.raises(SettingMisconfigured, match="Invalid type for TEST_DICT"):
        convert_and_validate("TEST_DICT", '{"a": [1, "b"]}', dict[str, list[int]])


def test_convert_and_validate_any_and_none_containers():
    assert convert_and_validate("TEST_LIST", '[1, "a", None]', list[Any]) == [
        1,
        "a",
        None,
    ]
    assert convert_and_validate("TEST_LIST", "[None, None]", list[None]) == [None, None]
    with pytest.raises(SettingMisconfigured, match="Invalid type for TEST_LIST"):
        convert_and_validate("TEST_LIST", "[None, 1]", list[None])


def test_convert_and_validate_union_with_literal_container():
    union_type = list[Union[Literal["a", "b"], int]]
    assert convert_and_validate("TEST_LIST", '[1, "a"]', union_type) == [1, "a"]
    with pytest.raises(SettingMisconfigured, match="Invalid type for TEST_LIST"):
        convert_and_validate("TEST_LIST", '["c"]', union_type)


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

    # Optional[int] must not accept arbitrary strings
    assert convert_and_validate("TEST_UNION", "42", Optional[int]) == 42
    with pytest.raises(SettingMisconfigured):
        convert_and_validate("TEST_UNION", "abc", Optional[int])


def test_convert_and_validate_literal_types():
    # String literals
    assert convert_and_validate("TEST_LITERAL", "a", Literal["a", "b"]) == "a"
    # Integer literals
    assert convert_and_validate("TEST_LITERAL", "1", Literal[1, 2]) == 1
    # The converted value keeps the literal's type
    assert convert_and_validate("TEST_LITERAL", "True", Literal[True]) is True
    # Mixed literals use the literal's own type, so "1" stays a string
    assert convert_and_validate("TEST_LITERAL", "1", Literal["1", 2]) == "1"
    assert type(convert_and_validate("TEST_LITERAL", "1", Literal["1", 2])) is str
    assert convert_and_validate("TEST_LITERAL", "2", Literal["1", 2]) == 2
    # None literals
    assert convert_and_validate("TEST_LITERAL", "None", Literal[None, "a"]) is None
    # A non-None value does not match a None literal
    with pytest.raises(SettingMisconfigured):
        convert_and_validate("TEST_LITERAL", "a", Literal[None])

    # Values outside the allowed literals are rejected
    with pytest.raises(SettingMisconfigured, match="Invalid type for TEST_LITERAL"):
        convert_and_validate("TEST_LITERAL", "c", Literal["a", "b"])
    with pytest.raises(SettingMisconfigured):
        convert_and_validate("TEST_LITERAL", "3", Literal[1, 2])
    # Booleans are not integers for Literal matching
    with pytest.raises(SettingMisconfigured):
        convert_and_validate("TEST_LITERAL", "True", Literal[1])


def test_convert_and_validate_literal_inside_union():
    union_type = Union[Literal["a", "b"], int]
    assert convert_and_validate("TEST_LITERAL", "a", union_type) == "a"
    assert convert_and_validate("TEST_LITERAL", "42", union_type) == 42
    with pytest.raises(SettingMisconfigured):
        convert_and_validate("TEST_LITERAL", "c", union_type)


def test_convert_and_validate_list_of_literals():
    # typing.List
    assert convert_and_validate(
        "TEST_LITERAL", '["a", "b"]', List[Literal["a", "b"]]
    ) == ["a", "b"]
    assert convert_and_validate("TEST_LITERAL", "[1, 3]", List[Literal[1, 2, 3]]) == [
        1,
        3,
    ]
    assert convert_and_validate("TEST_LITERAL", '["1", 2]', List[Literal["1", 2]]) == [
        "1",
        2,
    ]
    assert convert_and_validate("TEST_LITERAL", "[]", List[Literal["a"]]) == []
    with pytest.raises(SettingMisconfigured):
        convert_and_validate("TEST_LITERAL", '["a", "c"]', List[Literal["a", "b"]])
    with pytest.raises(SettingMisconfigured):
        convert_and_validate("TEST_LITERAL", "[1, 4]", List[Literal[1, 2, 3]])
    with pytest.raises(SettingMisconfigured):
        convert_and_validate("TEST_LITERAL", "[True]", List[Literal[1]])

    # built-in list
    assert convert_and_validate(
        "TEST_LITERAL", '["a", "b"]', list[Literal["a", "b"]]
    ) == ["a", "b"]
    assert convert_and_validate("TEST_LITERAL", "[1, 3]", list[Literal[1, 2, 3]]) == [
        1,
        3,
    ]
    assert convert_and_validate("TEST_LITERAL", '["1", 2]', list[Literal["1", 2]]) == [
        "1",
        2,
    ]
    assert convert_and_validate("TEST_LITERAL", "[]", list[Literal["a"]]) == []
    with pytest.raises(SettingMisconfigured):
        convert_and_validate("TEST_LITERAL", '["a", "c"]', list[Literal["a", "b"]])
    with pytest.raises(SettingMisconfigured):
        convert_and_validate("TEST_LITERAL", "[1, 4]", list[Literal[1, 2, 3]])
    with pytest.raises(SettingMisconfigured):
        convert_and_validate("TEST_LITERAL", "[True]", list[Literal[1]])


def test_convert_and_validate_containers_with_literals():
    assert convert_and_validate(
        "TEST_LITERAL", '{"a": 1}', Dict[Literal["a", "b"], Literal[1, 2]]
    ) == {"a": 1}
    assert convert_and_validate(
        "TEST_LITERAL", '("a", 2)', Tuple[Literal["a", "b"], Literal[1, 2]]
    ) == ("a", 2)

    with pytest.raises(SettingMisconfigured):
        convert_and_validate(
            "TEST_LITERAL", '{"a": 3}', Dict[Literal["a", "b"], Literal[1, 2]]
        )


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


def test_convert_and_validate_custom_class_quoted_annotation():
    converted = convert_and_validate(
        "TEST_CUSTOM", "[1, 2, 3]", QuotedAnnotationCustomClass
    )
    assert converted == QuotedAnnotationCustomClass([1, 2, 3])

    with pytest.raises(
        SettingMisconfigured, match="Invalid type for TEST_CUSTOM with configured value"
    ):
        convert_and_validate("TEST_CUSTOM", '["a", "b"]', QuotedAnnotationCustomClass)


def test_convert_and_validate_custom_class_postponed_annotations():
    converted = convert_and_validate("TEST_CUSTOM", "[1, 2, 3]", PostponedListOfInts)
    assert converted == PostponedListOfInts([1, 2, 3])

    with pytest.raises(
        SettingMisconfigured, match="Invalid type for TEST_CUSTOM with configured value"
    ):
        convert_and_validate("TEST_CUSTOM", '["a", "b"]', PostponedListOfInts)
