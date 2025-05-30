import os
from decimal import Decimal, InvalidOperation

import pytest

from pyttings import settings
from pyttings.core import Settings
from pyttings.exceptions import SettingMisconfigured
from tests.utils import ListOfInts, MultipleArgsCustomClass


@pytest.fixture(autouse=True)
def reset_settings_cache():
    settings._cache = {}


# Test missing settings module
def test_missing_settings_module(monkeypatch):
    monkeypatch.delenv("PYTTING_SETTINGS_MODULE")
    with pytest.raises(
        ValueError,
        match="'PYTTING_SETTINGS_MODULE' environment variable is not set.\nPlease specify a settings module.",
    ):
        Settings()


# Test not found/empty settings module
def test_not_found_settings_module(monkeypatch):
    monkeypatch.setenv("PYTTING_SETTINGS_MODULE", "not.found.settings.module")
    s = Settings()
    assert s._type_hints == {}


# Test missing attribute
def test_missing_attribute():
    with pytest.raises(AttributeError, match="has no attribute 'MISSING_SETTING'"):
        _ = settings.MISSING_SETTING


# Test custom prefix
def test_custom_prefix(monkeypatch):
    monkeypatch.setenv("PYTTING_ENV_PREFIX", "TEST_")
    monkeypatch.setenv("PYTTING_SETTINGS_MODULE", "tests.settings")
    monkeypatch.setenv("TEST_OTHER_SETTING", "test_value")
    new_settings = Settings()
    assert new_settings._env_prefix == "TEST_"
    assert new_settings.DEBUG is True
    assert new_settings.DATABASE_URL == "sqlite:///db.sqlite3"
    assert new_settings.OTHER_SETTING == "test_value"


# Test basic settings initialization
def test_settings_basic_values():
    assert settings.DEBUG is True
    assert settings.DATABASE_URL == "sqlite:///db.sqlite3"
    assert settings.SECRET_KEY == "my-secret-key"
    assert settings.PORT == 8000
    assert settings.ENABLE_FEATURE is False


def test_settings_collections():
    assert settings.SOME_LIST == ["a", "b", "c"]
    assert settings.SOME_TUPLE == ("a", "b", "c")
    assert settings.SOME_SET == {"a", "b", "c"}
    assert settings.SOME_DICT == {"a": "b", "c": "d"}


def test_settings_special_types():
    assert settings.NONE_VALUE is None
    assert settings.SOME_UNION_TYPE == "some_str"
    assert settings.SOME_DECIMAL == Decimal("1.0")
    assert settings.SOME_CUSTOM_CLASS == ListOfInts([1, 2, 3])
    assert settings.SOME_MULTIPLE_CUSTOM_CLASS == MultipleArgsCustomClass(1, "2", 3)


def test_settings_no_type_hints():
    assert settings.NO_TYPE_HINT_NONE is None
    assert settings.NO_TYPE_HINT_BOOL is True
    assert settings.NO_TYPE_HINT_INT == 1
    assert settings.NO_TYPE_HINT_FLOAT == 1.0
    assert settings.NO_TYPE_HINT_STR == "a"


def test_settings_no_type_hints_collections():
    assert settings.NO_TYPE_HINT_DICT == {"a": "b", "c": "d"}
    assert settings.NO_TYPE_HINT_LIST == ["a", "b", "c"]
    assert settings.NO_TYPE_HINT_TUPLE == ("a", "b", "c")
    assert settings.NO_TYPE_HINT_SET == {"a", "b", "c"}
    assert settings.NO_TYPE_HINT_DECIMAL == Decimal("1.0")


# Test environment variable overrides - basic types
def test_env_var_overrides_basic(monkeypatch):
    monkeypatch.setenv("PYTTING_DEBUG", "False")
    monkeypatch.setenv("PYTTING_DATABASE_URL", "postgresql://user:pass@localhost/db")
    monkeypatch.setenv("PYTTING_SECRET_KEY", "new-secret-key")
    monkeypatch.setenv("PYTTING_PORT", "8080")
    monkeypatch.setenv("PYTTING_ENABLE_FEATURE", "True")

    assert settings.DEBUG is False
    assert settings.DATABASE_URL == "postgresql://user:pass@localhost/db"
    assert settings.SECRET_KEY == "new-secret-key"
    assert settings.PORT == 8080
    assert settings.ENABLE_FEATURE is True


# Test environment variable overrides - collections
def test_env_var_overrides_collections(monkeypatch):
    monkeypatch.setenv("PYTTING_SOME_LIST", '["x", "y"]')
    monkeypatch.setenv("PYTTING_SOME_TUPLE", '("x", "y")')
    monkeypatch.setenv("PYTTING_SOME_SET", '{"x", "y"}')
    monkeypatch.setenv("PYTTING_SOME_DICT", '{"x": "y"}')

    assert settings.SOME_LIST == ["x", "y"]
    assert settings.SOME_TUPLE == ("x", "y")
    assert settings.SOME_SET == {"x", "y"}
    assert settings.SOME_DICT == {"x": "y"}


# Test environment variable overrides - special types
def test_env_var_overrides_special_types(monkeypatch):
    monkeypatch.setenv("PYTTING_NONE_VALUE", "some_value")
    monkeypatch.setenv("PYTTING_SOME_UNION_TYPE", "some_other_str")
    monkeypatch.setenv("PYTTING_SOME_DECIMAL", "2.0")

    assert settings.NONE_VALUE == "some_value"
    assert settings.SOME_UNION_TYPE == "some_other_str"
    assert settings.SOME_DECIMAL == Decimal("2.0")


# Test environment variable overrides - custom classes
def test_env_var_overrides_custom_classes(monkeypatch):
    monkeypatch.setenv("PYTTING_SOME_CUSTOM_CLASS", "[1, 2, 3, 4]")
    monkeypatch.setenv(
        "PYTTING_SOME_MULTIPLE_CUSTOM_CLASS",
        '{"int_value": 3, "str_value": "2", "value": "1"}',
    )

    assert settings.SOME_CUSTOM_CLASS == ListOfInts([1, 2, 3, 4])
    assert settings.SOME_MULTIPLE_CUSTOM_CLASS == MultipleArgsCustomClass(3, "2", "1")


# Test environment variable overrides - no type hints
def test_env_var_overrides_no_type_hint_simple(monkeypatch):
    monkeypatch.setenv("PYTTING_NO_TYPE_HINT_NONE", "tests.settings")
    monkeypatch.setenv("PYTTING_NO_TYPE_HINT_BOOL", "False")
    monkeypatch.setenv("PYTTING_NO_TYPE_HINT_INT", "42")
    monkeypatch.setenv("PYTTING_NO_TYPE_HINT_FLOAT", "3.14")
    monkeypatch.setenv("PYTTING_NO_TYPE_HINT_STR", "override")

    assert settings.NO_TYPE_HINT_NONE == "tests.settings"
    assert settings.NO_TYPE_HINT_BOOL is False
    assert settings.NO_TYPE_HINT_INT == 42
    assert settings.NO_TYPE_HINT_FLOAT == 3.14
    assert settings.NO_TYPE_HINT_STR == "override"


def test_env_var_overrides_no_type_hint_collections(monkeypatch):
    monkeypatch.setenv("PYTTING_NO_TYPE_HINT_DICT", '{"x": "y"}')
    monkeypatch.setenv("PYTTING_NO_TYPE_HINT_LIST", '["x", "y"]')
    monkeypatch.setenv("PYTTING_NO_TYPE_HINT_TUPLE", '("x", "y")')
    monkeypatch.setenv("PYTTING_NO_TYPE_HINT_SET", '{"x", "y"}')
    monkeypatch.setenv("PYTTING_NO_TYPE_HINT_DECIMAL", "3.14")

    assert settings.NO_TYPE_HINT_DICT == {"x": "y"}
    assert settings.NO_TYPE_HINT_LIST == ["x", "y"]
    assert settings.NO_TYPE_HINT_TUPLE == ("x", "y")
    assert settings.NO_TYPE_HINT_SET == {"x", "y"}
    assert settings.NO_TYPE_HINT_DECIMAL == Decimal("3.14")


# Test complex environment variable type conversions
def test_env_var_type_conversion_collections(monkeypatch):
    monkeypatch.setenv("PYTTING_SOME_LIST", '["a", "b", "c", "d"]')
    monkeypatch.setenv("PYTTING_SOME_TUPLE", "(1,2,3)")
    monkeypatch.setenv("PYTTING_SOME_SET", '{"a", "b", "c", 1, 2, 3}')

    assert settings.SOME_LIST == ["a", "b", "c", "d"]
    assert settings.SOME_TUPLE == (1, 2, 3)
    assert settings.SOME_SET == {"a", "b", "c", 1, 2, 3}


def test_env_var_type_conversion_complex_dict(monkeypatch):
    monkeypatch.setenv(
        "PYTTING_SOME_DICT",
        '{"a": "b", "c": "d", "another_dict": {"a": 1, "b": 2, "c": 3}}',
    )

    assert settings.SOME_DICT == {
        "a": "b",
        "c": "d",
        "another_dict": {"a": 1, "b": 2, "c": 3},
    }


# Test union type conversion
def test_env_var_type_conversion_union_str(monkeypatch):
    monkeypatch.setenv("PYTTING_SOME_UNION_TYPE", "some_other_str")
    assert settings.SOME_UNION_TYPE == "some_other_str"


def test_env_var_type_conversion_union_dict(monkeypatch):
    monkeypatch.setenv("PYTTING_SOME_UNION_TYPE", '{"x": "y"}')
    assert settings.SOME_UNION_TYPE == {"x": "y"}


# Test strict type checking
def test_env_var_type_conversion_strict_valid(monkeypatch):
    monkeypatch.setenv("PYTTING_SOME_STRICT_DICT", '{"x": "y"}')
    monkeypatch.setenv("PYTTING_SOME_STRICT_LIST", '["x", "y"]')

    assert settings.SOME_STRICT_DICT == {"x": "y"}
    assert settings.SOME_STRICT_LIST == ["x", "y"]


def test_env_var_type_conversion_strict_list_invalid(monkeypatch):
    monkeypatch.setenv("PYTTING_SOME_STRICT_LIST", "[1, 'x', 'y']")

    with pytest.raises(
        SettingMisconfigured,
        match=r"Invalid type for SOME_STRICT_LIST with configured value '.*'\.\nExpected list\[str\]\.",
    ):
        _ = settings.SOME_STRICT_LIST


def test_env_var_type_conversion_strict_dict_invalid_key(monkeypatch):
    monkeypatch.setenv("PYTTING_SOME_STRICT_DICT", "{1: 1}")

    with pytest.raises(
        SettingMisconfigured,
        match=r"Invalid type for SOME_STRICT_DICT with configured value '.*'\.\nExpected dict\[str, str\].",
    ):
        _ = settings.SOME_STRICT_DICT


def test_env_var_type_conversion_strict_dict_invalid_value(monkeypatch):
    monkeypatch.setenv("PYTTING_SOME_STRICT_DICT", "{'x': 1}")

    with pytest.raises(
        SettingMisconfigured,
        match=r"Invalid type for SOME_STRICT_DICT with configured value '.*'\.\nExpected dict\[str, str\].",
    ):
        _ = settings.SOME_STRICT_DICT


def test_env_var_type_conversion_strict_dict_invalid_key_type(monkeypatch):
    monkeypatch.setenv("PYTTING_SOME_STRICT_DICT", "{1: 'x'}")

    with pytest.raises(
        SettingMisconfigured,
        match=r"Invalid type for SOME_STRICT_DICT with configured value '.*'\.\nExpected dict\[str, str\].",
    ):
        _ = settings.SOME_STRICT_DICT


# Test custom class validation
def test_env_var_type_conversion_strict_custom_class_invalid_list(monkeypatch):
    monkeypatch.setenv("PYTTING_SOME_CUSTOM_CLASS", '[1, 2, 3, "4"]')

    with pytest.raises(
        SettingMisconfigured,
        match=r"Invalid type for SOME_CUSTOM_CLASS with configured value '.*'\.\nExpected list\[int\]\.",
    ):
        _ = settings.SOME_CUSTOM_CLASS


def test_env_var_type_conversion_strict_custom_class_invalid_dict(monkeypatch):
    monkeypatch.setenv(
        "PYTTING_SOME_MULTIPLE_CUSTOM_CLASS",
        '{"int_value": [1], "str_value": "2", "value": "1"}',
    )

    with pytest.raises(
        SettingMisconfigured,
        match=r"Invalid type for SOME_MULTIPLE_CUSTOM_CLASS with configured value '.*'\.\nExpected dict\[str, int \| str\]\.",
    ):
        _ = settings.SOME_MULTIPLE_CUSTOM_CLASS


# Test type conversion failures
def test_env_var_type_conversion_failure_list(monkeypatch):
    monkeypatch.setenv("PYTTING_SOME_LIST", "1")

    with pytest.raises(
        SettingMisconfigured,
        match="Invalid type for SOME_LIST with configured value '1'.\nExpected <class 'list'>.",
    ):
        _ = settings.SOME_LIST


def test_env_var_type_conversion_failure_tuple(monkeypatch):
    monkeypatch.setenv("PYTTING_SOME_TUPLE", "a")

    with pytest.raises(
        SettingMisconfigured,
        match="Invalid type for SOME_TUPLE with configured value 'a'.\nExpected <class 'tuple'>.",
    ):
        _ = settings.SOME_TUPLE


def test_env_var_type_conversion_failure_int(monkeypatch):
    monkeypatch.setenv("PYTTING_PORT", "")

    with pytest.raises(
        SettingMisconfigured,
        match="Invalid type for PORT with configured value ''.\nExpected <class 'int'>.",
    ):
        _ = settings.PORT


def test_env_var_type_conversion_failure_dict(monkeypatch):
    monkeypatch.setenv("PYTTING_NO_TYPE_HINT_DICT", "123")

    with pytest.raises(
        SettingMisconfigured,
        match="Invalid type for NO_TYPE_HINT_DICT with configured value '123'.\nExpected <class 'dict'>.",
    ):
        _ = settings.NO_TYPE_HINT_DICT


def test_env_var_type_conversion_failure_decimal(monkeypatch):
    monkeypatch.setenv("PYTTING_NO_TYPE_HINT_DECIMAL", "A")

    with pytest.raises(InvalidOperation):
        _ = settings.NO_TYPE_HINT_DECIMAL


# Test eager loading
def test_settings_eager_loading():
    eager_settings = Settings(lazy_load=False)
    assert eager_settings._cache == eager_settings.defaults


def test_settings_eager_loading_override(monkeypatch):
    monkeypatch.setenv("PYTTING_DEBUG", "False")
    eager_settings = Settings(lazy_load=False)
    assert "DEBUG" in eager_settings._cache


def test_env_var_type_conversion_strict_list_invalid_eager(monkeypatch):
    monkeypatch.setenv("PYTTING_SOME_STRICT_LIST", "[1, 'x', 'y']")
    with pytest.raises(
        SettingMisconfigured,
        match=r"Invalid type for SOME_STRICT_LIST with configured value '.*'\.\nExpected list\[str\]\.",
    ):
        _ = Settings(lazy_load=False)


def test_env_var_type_conversion_failure_decimal_eager(monkeypatch):
    monkeypatch.setenv("PYTTING_NO_TYPE_HINT_DECIMAL", "A")
    with pytest.raises(InvalidOperation):
        _ = Settings(lazy_load=False)


def test_env_var_type_conversion_strict_custom_class_invalid_list_eager(monkeypatch):
    monkeypatch.setenv("PYTTING_SOME_CUSTOM_CLASS", '[1, 2, 3, "4"]')

    with pytest.raises(
        SettingMisconfigured,
        match=r"Invalid type for SOME_CUSTOM_CLASS with configured value '.*'\.\nExpected list\[int\]\.",
    ):
        _ = Settings(lazy_load=False)
