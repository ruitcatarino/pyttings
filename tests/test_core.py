import os

import pytest

from pyttings import settings
from pyttings.core import SettingMisconfigured, Settings


@pytest.fixture(autouse=True)
def clear_settings_cache():
    settings._cache = {}


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


# Test environment variable overrides
def test_env_var_overrides():
    os.environ["PYTTING_DEBUG"] = "False"
    os.environ["PYTTING_PORT"] = "8080"
    os.environ["PYTTING_NONE_VALUE"] = "some_value"
    assert settings.DEBUG is False
    assert settings.PORT == 8080
    assert settings.NONE_VALUE == "some_value"


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


# Test environment variable type conversion
def test_env_var_type_conversion():
    os.environ["PYTTING_ENABLE_FEATURE"] = "True"
    os.environ["PYTTING_SOME_LIST"] = '["a","b","c","d"]'
    os.environ["PYTTING_SOME_TUPLE"] = "(1,2,3)"
    os.environ["PYTTING_SOME_SET"] = '{"a","b","c",1,2,3}'
    os.environ["PYTTING_SOME_DICT"] = (
        '{"a":"b","c":"d","another_dict":{"a":1,"b":2,"c":3}}'
    )
    assert settings.ENABLE_FEATURE is True
    assert settings.SOME_LIST == ["a", "b", "c", "d"]
    assert settings.SOME_TUPLE == (1, 2, 3)
    assert settings.SOME_SET == {"a", "b", "c", 1, 2, 3}
    assert settings.SOME_DICT == {
        "a": "b",
        "c": "d",
        "another_dict": {"a": 1, "b": 2, "c": 3},
    }


# Test failure to convert environment variable
def test_env_var_type_conversion_failure():
    os.environ["PYTTING_SOME_LIST"] = "1"
    os.environ["PYTTING_SOME_TUPLE"] = "a"
    os.environ["PYTTING_PORT"] = ""
    with pytest.raises(
        SettingMisconfigured,
        match="Invalid type for SOME_LIST with configured value '1'.\nExpected type list.",
    ):
        _ = settings.SOME_LIST

    with pytest.raises(
        SettingMisconfigured,
        match="Invalid type for SOME_TUPLE with configured value 'a'.\nExpected type tuple.",
    ):
        _ = settings.SOME_TUPLE

    with pytest.raises(
        SettingMisconfigured,
        match="Invalid type for PORT with configured value ''.\nExpected type int.",
    ):
        _ = settings.PORT


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
