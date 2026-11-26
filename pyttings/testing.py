import inspect
from contextlib import ExitStack
from functools import wraps
from types import TracebackType
from typing import Any, Callable, TypeVar, cast

from pyttings.core import Settings

_T = TypeVar("_T")

_WRAPPED_METHODS = frozenset(
    {
        "asyncSetUp",
        "asyncTearDown",
        "setUp",
        "setup_method",
        "tearDown",
        "teardown_method",
    }
)


class override_settings:
    """Temporarily override settings in tests.

    Works as a context manager and as a function or class decorator. Values
    are applied to the shared settings cache and restored on exit, even when
    an exception is raised. Overrides take precedence over environment
    variables, do not modify ``os.environ``, and can be nested.

    Class decorators wrap ``test*`` methods and common setup/teardown methods,
    not class-level fixtures. Unknown setting names are restored or removed on
    exit. Overrides mutate the shared cache, so they are not thread-safe.
    """

    def __init__(self, **overrides: Any) -> None:
        self.overrides = overrides
        self._stack = ExitStack()

    def __enter__(self) -> Settings:
        from pyttings import settings

        return self._stack.enter_context(settings.override(**self.overrides))

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        return self._stack.__exit__(exc_type, exc_value, traceback)

    def __call__(self, target: _T) -> _T:
        if inspect.isclass(target):
            return cast(_T, _decorate_class(target, self._recreate_cm))
        func = cast(Callable[..., Any], target)
        return cast(_T, _wrap_callable(func, self._recreate_cm))

    def _recreate_cm(self) -> "override_settings":
        return type(self)(**self.overrides)


def _wrap_callable(
    func: Callable[..., Any],
    factory: Callable[[], override_settings],
) -> Callable[..., Any]:
    """Wrap a sync or async callable in an override context."""

    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        with factory():
            return func(*args, **kwargs)

    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        with factory():
            return await func(*args, **kwargs)

    return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper


def _decorate_class(cls: _T, factory: Callable[[], override_settings]) -> _T:
    """Wrap test and setup/teardown methods on a test class."""
    for name in dir(cls):
        if not (name.startswith("test") or name in _WRAPPED_METHODS):
            continue
        raw = inspect.getattr_static(cls, name)
        if inspect.isfunction(raw):
            setattr(cls, name, _wrap_callable(raw, factory))
    return cls
