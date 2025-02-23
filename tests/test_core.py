import os
from decimal import Decimal, InvalidOperation

import pytest

from pyttings import settings
from pyttings.core import Settings
from pyttings.exceptions import SettingMisconfigured
from tests.utils import ListOfInts, MultipleArgsCustomClass


@pytest.fixture(autouse=True)
def clear_settings_cache():
    settings._cache = {}


# Test missing settings module
def test_missing_settings_module():
    del os.environ["PYTTING_SETTINGS_MODULE"]
    with pytest.raises(
        ValueError,
        match="'PYTTING_SETTINGS_MODULE' environment variable is not set.\nPlease specify a settings module.",
    ):
        Settings()


# Test missing attribute
def test_missing_attribute():
    with pytest.raises(AttributeError, match="has no attribute 'MISSING_SETTING'"):
        _ = settings.MISSING_SETTING


# Test custom prefix
def test_custom_prefix():
    os.environ["PYTTING_ENV_PREFIX"] = "TEST_"
    os.environ["PYTTING_SETTINGS_MODULE"] = "tests.settings"
    os.environ["TEST_OTHER_SETTING"] = "test_value"
    new_settings = Settings()
    assert new_settings._env_prefix == "TEST_"
    assert new_settings.DEBUG is True
    assert new_settings.DATABASE_URL == "sqlite:///db.sqlite3"
    assert new_settings.OTHER_SETTING == "test_value"


# Test settings initialization
def test_settings_initialization():
    assert settings.DEBUG is True
    assert settings.DATABASE_URL == "sqlite:///db.sqlite3"
    assert settings.SECRET_KEY == "my-secret-key"
    assert settings.PORT == 8000
    assert settings.ENABLE_FEATURE is False
    assert settings.SOME_LIST == ["a", "b", "c"]
    assert settings.SOME_TUPLE == ("a", "b", "c")
    assert settings.SOME_SET == {"a", "b", "c"}
    assert settings.SOME_DICT == {"a": "b", "c": "d"}
    assert settings.NONE_VALUE is None
    assert settings.SOME_UNION_TYPE == "some_str"
    assert settings.SOME_DECIMAL == Decimal("1.0")
    assert settings.SOME_CUSTOM_CLASS == ListOfInts([1, 2, 3])
    assert settings.SOME_MULTIPLE_CUSTOM_CLASS == MultipleArgsCustomClass(1, "2", 3)
    assert settings.NO_TYPE_HINT_NONE is None
    assert settings.NO_TYPE_HINT_BOOL is True
    assert settings.NO_TYPE_HINT_INT == 1
    assert settings.NO_TYPE_HINT_FLOAT == 1.0
    assert settings.NO_TYPE_HINT_STR == "a"
    assert settings.NO_TYPE_HINT_DICT == {"a": "b", "c": "d"}
    assert settings.NO_TYPE_HINT_LIST == ["a", "b", "c"]
    assert settings.NO_TYPE_HINT_TUPLE == ("a", "b", "c")
    assert settings.NO_TYPE_HINT_SET == {"a", "b", "c"}
    assert settings.NO_TYPE_HINT_DECIMAL == Decimal("1.0")


# Test environment variable overrides
def test_env_var_overrides():
    os.environ["PYTTING_DEBUG"] = "False"
    os.environ["PYTTING_DATABASE_URL"] = "postgresql://user:pass@localhost/db"
    os.environ["PYTTING_SECRET_KEY"] = "new-secret-key"
    os.environ["PYTTING_PORT"] = "8080"
    os.environ["PYTTING_ENABLE_FEATURE"] = "True"
    os.environ["PYTTING_SOME_LIST"] = '["x", "y"]'
    os.environ["PYTTING_SOME_TUPLE"] = '("x", "y")'
    os.environ["PYTTING_SOME_SET"] = '{"x", "y"}'
    os.environ["PYTTING_SOME_DICT"] = '{"x": "y"}'
    os.environ["PYTTING_NONE_VALUE"] = "some_value"
    os.environ["PYTTING_SOME_UNION_TYPE"] = "some_other_str"
    os.environ["PYTTING_SOME_DECIMAL"] = "2.0"
    os.environ["PYTTING_SOME_CUSTOM_CLASS"] = "[1, 2, 3, 4]"
    os.environ["PYTTING_SOME_MULTIPLE_CUSTOM_CLASS"] = (
        '{"int_value": 3, "str_value": "2", "value": "1"}'
    )

    assert settings.DEBUG is False
    assert settings.DATABASE_URL == "postgresql://user:pass@localhost/db"
    assert settings.SECRET_KEY == "new-secret-key"
    assert settings.PORT == 8080
    assert settings.ENABLE_FEATURE is True
    assert settings.SOME_LIST == ["x", "y"]
    assert settings.SOME_TUPLE == ("x", "y")
    assert settings.SOME_SET == {"x", "y"}
    assert settings.SOME_DICT == {"x": "y"}
    assert settings.NONE_VALUE == "some_value"
    assert settings.SOME_UNION_TYPE == "some_other_str"
    assert settings.SOME_DECIMAL == Decimal("2.0")
    assert settings.SOME_CUSTOM_CLASS == ListOfInts([1, 2, 3, 4])
    assert settings.SOME_MULTIPLE_CUSTOM_CLASS == MultipleArgsCustomClass(3, "2", "1")


# Test environment variable overrides with no type hint
def test_env_var_overrides_no_type_hint():
    os.environ["PYTTING_NO_TYPE_HINT_NONE"] = "tests.settings"
    os.environ["PYTTING_NO_TYPE_HINT_BOOL"] = "False"
    os.environ["PYTTING_NO_TYPE_HINT_INT"] = "42"
    os.environ["PYTTING_NO_TYPE_HINT_FLOAT"] = "3.14"
    os.environ["PYTTING_NO_TYPE_HINT_STR"] = "override"
    os.environ["PYTTING_NO_TYPE_HINT_DICT"] = '{"x": "y"}'
    os.environ["PYTTING_NO_TYPE_HINT_LIST"] = '["x", "y"]'
    os.environ["PYTTING_NO_TYPE_HINT_TUPLE"] = '("x", "y")'
    os.environ["PYTTING_NO_TYPE_HINT_SET"] = '{"x", "y"}'
    os.environ["PYTTING_NO_TYPE_HINT_DECIMAL"] = "3.14"

    assert settings.NO_TYPE_HINT_NONE == "tests.settings"
    assert settings.NO_TYPE_HINT_BOOL is False
    assert settings.NO_TYPE_HINT_INT == 42
    assert settings.NO_TYPE_HINT_FLOAT == 3.14
    assert settings.NO_TYPE_HINT_STR == "override"
    assert settings.NO_TYPE_HINT_DICT == {"x": "y"}
    assert settings.NO_TYPE_HINT_LIST == ["x", "y"]
    assert settings.NO_TYPE_HINT_TUPLE == ("x", "y")
    assert settings.NO_TYPE_HINT_SET == {"x", "y"}
    assert settings.NO_TYPE_HINT_DECIMAL == Decimal("3.14")


# Test environment variable type conversion
def test_env_var_type_conversion():
    os.environ["PYTTING_ENABLE_FEATURE"] = "True"
    os.environ["PYTTING_SOME_LIST"] = '["a", "b", "c", "d"]'
    os.environ["PYTTING_SOME_TUPLE"] = "(1,2,3)"
    os.environ["PYTTING_SOME_SET"] = '{"a", "b", "c", 1, 2, 3}'
    os.environ["PYTTING_SOME_DICT"] = (
        '{"a": "b", "c": "d", "another_dict": {"a": 1, "b": 2, "c": 3}}'
    )
    os.environ["PYTTING_DEBUG"] = "False"
    os.environ["PYTTING_DATABASE_URL"] = "mysql://user:pass@localhost/db"
    os.environ["PYTTING_SECRET_KEY"] = "another-secret-key"
    os.environ["PYTTING_PORT"] = "9090"

    assert settings.ENABLE_FEATURE is True
    assert settings.SOME_LIST == ["a", "b", "c", "d"]
    assert settings.SOME_TUPLE == (1, 2, 3)
    assert settings.SOME_SET == {"a", "b", "c", 1, 2, 3}
    assert settings.SOME_DICT == {
        "a": "b",
        "c": "d",
        "another_dict": {"a": 1, "b": 2, "c": 3},
    }
    assert settings.DEBUG is False
    assert settings.DATABASE_URL == "mysql://user:pass@localhost/db"
    assert settings.SECRET_KEY == "another-secret-key"
    assert settings.PORT == 9090


# Test environment variable type conversion with no type hint
def test_env_var_type_conversion_no_type_hint():
    os.environ["PYTTING_NO_TYPE_HINT_INT"] = "99"
    os.environ["PYTTING_NO_TYPE_HINT_FLOAT"] = "2.71"
    os.environ["PYTTING_NO_TYPE_HINT_BOOL"] = "True"
    os.environ["PYTTING_NO_TYPE_HINT_STR"] = "new_value"
    os.environ["PYTTING_NO_TYPE_HINT_LIST"] = '["new", "list"]'
    os.environ["PYTTING_NO_TYPE_HINT_TUPLE"] = '("new", "tuple")'
    os.environ["PYTTING_NO_TYPE_HINT_SET"] = '{"new", "set"}'
    os.environ["PYTTING_NO_TYPE_HINT_DICT"] = '{"new": "dict"}'

    assert settings.NO_TYPE_HINT_INT == 99
    assert settings.NO_TYPE_HINT_FLOAT == 2.71
    assert settings.NO_TYPE_HINT_BOOL is True
    assert settings.NO_TYPE_HINT_STR == "new_value"
    assert settings.NO_TYPE_HINT_LIST == ["new", "list"]
    assert settings.NO_TYPE_HINT_TUPLE == ("new", "tuple")
    assert settings.NO_TYPE_HINT_SET == {"new", "set"}
    assert settings.NO_TYPE_HINT_DICT == {"new": "dict"}


# Test environment variable type conversion with union type
def test_env_var_type_conversion_union():
    os.environ["PYTTING_SOME_UNION_TYPE"] = "some_other_str"
    assert settings.SOME_UNION_TYPE == "some_other_str"
    settings._cache.pop("SOME_UNION_TYPE")
    os.environ["PYTTING_SOME_UNION_TYPE"] = '{"x": "y"}'
    assert settings.SOME_UNION_TYPE == {"x": "y"}


def test_env_var_type_conversion_strict():
    os.environ["PYTTING_SOME_STRICT_DICT"] = '{"x": "y"}'
    os.environ["PYTTING_SOME_STRICT_LIST"] = '["x", "y"]'
    assert settings.SOME_STRICT_DICT == {"x": "y"}
    assert settings.SOME_STRICT_LIST == ["x", "y"]

    settings._cache.pop("SOME_STRICT_LIST")
    os.environ["PYTTING_SOME_STRICT_LIST"] = "[1, 'x', 'y']"
    with pytest.raises(
        SettingMisconfigured,
        match=r"Invalid type for SOME_STRICT_LIST with configured value '.*'\.\nExpected list\[str\]\.",
    ):
        _ = settings.SOME_STRICT_LIST

    settings._cache.pop("SOME_STRICT_DICT")
    os.environ["PYTTING_SOME_STRICT_DICT"] = "{1: 1}"
    with pytest.raises(
        SettingMisconfigured,
        match=r"Invalid type for SOME_STRICT_DICT with configured value '.*'\.\nExpected dict\[str, str\].",
    ):
        _ = settings.SOME_STRICT_DICT

    os.environ["PYTTING_SOME_STRICT_DICT"] = "{'x': 1}"
    with pytest.raises(
        SettingMisconfigured,
        match=r"Invalid type for SOME_STRICT_DICT with configured value '.*'\.\nExpected dict\[str, str\].",
    ):
        _ = settings.SOME_STRICT_DICT

    os.environ["PYTTING_SOME_STRICT_DICT"] = "{1: 'x'}"
    with pytest.raises(
        SettingMisconfigured,
        match=r"Invalid type for SOME_STRICT_DICT with configured value '.*'\.\nExpected dict\[str, str\].",
    ):
        _ = settings.SOME_STRICT_DICT


# Test environment variable type conversion with custom class
def test_env_var_type_conversion_strict_custom_class():
    os.environ["PYTTING_SOME_CUSTOM_CLASS"] = '[1, 2, 3, "4"]'
    os.environ["PYTTING_SOME_MULTIPLE_CUSTOM_CLASS"] = (
        '{"int_value": [1], "str_value": "2", "value": "1"}'
    )
    with pytest.raises(
        SettingMisconfigured,
        match=r"Invalid type for SOME_CUSTOM_CLASS with configured value '.*'\.\nExpected list\[int\]\.",
    ):
        _ = settings.SOME_CUSTOM_CLASS
    with pytest.raises(
        SettingMisconfigured,
        match=r"Invalid type for SOME_MULTIPLE_CUSTOM_CLASS with configured value '.*'\.\nExpected dict\[str, int \| str\]\.",
    ):
        _ = settings.SOME_MULTIPLE_CUSTOM_CLASS


# Test failure to convert environment variable
def test_env_var_type_conversion_failure():
    os.environ["PYTTING_SOME_LIST"] = "1"
    os.environ["PYTTING_SOME_TUPLE"] = "a"
    os.environ["PYTTING_PORT"] = ""
    os.environ["PYTTING_NO_TYPE_HINT_DICT"] = "123"
    os.environ["PYTTING_NO_TYPE_HINT_DECIMAL"] = "A"
    with pytest.raises(
        SettingMisconfigured,
        match="Invalid type for SOME_LIST with configured value '1'.\nExpected <class 'list'>.",
    ):
        _ = settings.SOME_LIST

    with pytest.raises(
        SettingMisconfigured,
        match="Invalid type for SOME_TUPLE with configured value 'a'.\nExpected <class 'tuple'>.",
    ):
        _ = settings.SOME_TUPLE

    with pytest.raises(
        SettingMisconfigured,
        match="Invalid type for PORT with configured value ''.\nExpected <class 'int'>.",
    ):
        _ = settings.PORT

    with pytest.raises(
        SettingMisconfigured,
        match="Invalid type for NO_TYPE_HINT_DICT with configured value '123'.\nExpected <class 'dict'>.",
    ):
        _ = settings.NO_TYPE_HINT_DICT

    with pytest.raises(InvalidOperation):
        _ = settings.NO_TYPE_HINT_DECIMAL
