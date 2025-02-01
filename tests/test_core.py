import os

import pytest

from pyttings import settings
from pyttings.core import Settings


@pytest.fixture(autouse=True)
def clear_settings_cache():
    settings._cache = {}


# Test settings initialization
def test_settings_initialization():
    assert settings.DEBUG is True
    assert settings.DATABASE_URL == "sqlite:///db.sqlite3"
    assert settings.SECRET_KEY == "my-secret-key"


# Test environment variable overrides
def test_env_var_overrides():
    os.environ["PYTTING_DEBUG"] = "False"
    os.environ["PYTTING_PORT"] = "8080"
    print(os.environ["PYTTING_DEBUG"])
    print(settings._cache)
    assert settings.DEBUG is False  # Overridden by environment variable
    assert settings.PORT == 8080  # Overridden and converted to int


# Test missing settings module
def test_missing_settings_module():
    if "PYTTING_SETTINGS_MODULE" in os.environ:
        del os.environ["PYTTING_SETTINGS_MODULE"]
    with pytest.raises(
        ValueError, match="PYTTING_SETTINGS_MODULE environment variable is not set"
    ):
        Settings()


# Test missing attribute
def test_missing_attribute():
    with pytest.raises(AttributeError, match="has no attribute 'MISSING_SETTING'"):
        _ = settings.MISSING_SETTING


# Test environment variable type conversion
def test_env_var_type_conversion():
    os.environ["PYTTING_ENABLE_FEATURE"] = "True"
    assert settings.ENABLE_FEATURE is True  # Converted to bool


# Test custom prefix
def test_custom_prefix():
    os.environ["PYTTING_ENV_PREFIX"] = "TEST_"
    os.environ["PYTTING_SETTINGS_MODULE"] = "tests.settings"
    new_settings = Settings()
    assert new_settings._env_prefix == "TEST_"
    assert new_settings.DEBUG is True
    assert new_settings.DATABASE_URL == "sqlite:///db.sqlite3"
