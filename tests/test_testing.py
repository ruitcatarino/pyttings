import asyncio
import os

import pytest

from pyttings import override_settings, settings, typed_settings
from pyttings.core import Settings
from tests import settings as settings_module


def test_context_manager_with_nesting():
    assert settings.DEBUG is True
    with override_settings(DEBUG=False):
        assert settings.DEBUG is False
        with override_settings(DEBUG=True, PORT=1):
            assert (settings.DEBUG, settings.PORT) == (True, 1)
        assert (settings.DEBUG, settings.PORT) == (False, 8000)
    assert settings.DEBUG is True


def test_restores_on_exception():
    with pytest.raises(RuntimeError):
        with override_settings(DEBUG=False):
            assert settings.DEBUG is False
            raise RuntimeError("boom")
    assert settings.DEBUG is True


def test_decorator_is_reusable():
    decorator = override_settings(DEBUG=False, PORT=9000)

    @decorator
    def first():
        assert (settings.DEBUG, settings.PORT) == (False, 9000)

    @decorator
    def second():
        assert (settings.DEBUG, settings.PORT) == (False, 9000)

    for check in (first, second):
        check()
        assert (settings.DEBUG, settings.PORT) == (True, 8000)


def test_wins_over_environment_without_modifying_it(monkeypatch):
    # DEBUG was cached at import; drop it so the env var is read again.
    monkeypatch.setattr(settings, "_cache", {})
    monkeypatch.setenv("PYTTING_DEBUG", "False")
    assert settings.DEBUG is False

    with override_settings(DEBUG=True):
        assert settings.DEBUG is True
        assert os.environ["PYTTING_DEBUG"] == "False"
    assert settings.DEBUG is False
    assert os.environ["PYTTING_DEBUG"] == "False"


def test_unknown_name():
    with override_settings(NOT_DECLARED=123):
        assert settings.NOT_DECLARED == 123

    with pytest.raises(AttributeError):
        _ = settings.NOT_DECLARED


def test_applies_to_typed_settings():
    typed = typed_settings(settings_module)

    with override_settings(DEBUG=False):
        assert typed.DEBUG is False
    assert typed.DEBUG is True


def test_settings_override_method_lazy():
    lazy_settings = Settings(lazy_load=True)

    with lazy_settings.override(DEBUG=False):
        assert lazy_settings.DEBUG is False
    assert lazy_settings.DEBUG is True


def test_class_decorator_wraps_tests_and_setup_teardown():
    @override_settings(DEBUG=False)
    class Example:
        test_data = 1

        @property
        def test_property(self):
            return settings.DEBUG

        @staticmethod
        def test_static():
            return settings.DEBUG

        @classmethod
        def test_class(cls):
            return settings.DEBUG

        def setUp(self):
            assert settings.DEBUG is False

        def tearDown(self):
            assert settings.DEBUG is False

        def test_method(self):
            assert settings.DEBUG is False

        def helper(self):
            return settings.DEBUG

    example = Example()
    example.setUp()
    example.test_method()
    example.tearDown()
    assert example.helper() is True
    assert Example.test_data == 1
    assert Example.test_static() is True
    assert Example.test_class() is True
    assert example.test_property is True
    assert settings.DEBUG is True


def test_async_decorators():
    @override_settings(DEBUG=False)
    async def check():
        assert settings.DEBUG is False

    asyncio.run(check())
    assert settings.DEBUG is True

    @override_settings(DEBUG=False)
    class Example:
        async def test_method(self):
            assert settings.DEBUG is False

    asyncio.run(Example().test_method())
    assert settings.DEBUG is True
