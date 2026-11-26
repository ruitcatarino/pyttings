# Pyttings
[![Coverage Status](https://coveralls.io/repos/github/ruitcatarino/pyttings/badge.svg?branch=main)](https://coveralls.io/github/ruitcatarino/pyttings?branch=main)

Lightweight Python settings management with namespacing and modular files. Inspired by Django.

## Features

- **Namespaced Settings**: Use a prefix (e.g., `PYTTING_`) to avoid conflicts.
- **Custom Prefix**: Change the prefix using `PYTTING_ENV_PREFIX`.
- **Modular Settings**: Load settings from a module with `PYTTING_SETTINGS_MODULE`.
- **Environment Variables**: Override settings easily, with automatic type parsing.
- **Type Hint Support**: Converts environment variables to the expected type (recommended but not required).
- **Union Type Support**: Supports multiple possible types for a setting.
- **Literal Type Support**: Restricts a setting to a fixed set of allowed values (e.g. strings or integers).
- **Collection Type Validation**: Ensures list, tuple, set, and dict elements match expected types.
- **Custom Class Parsers**: Use a `__pyttings_convert__` method (or a custom-defined method) to parse settings into custom objects, configurable via `PYTTING_CUSTOM_CLASS_METHOD_NAME`.
- **Test Overrides**: Temporarily override settings with an `override_settings` decorator or context manager.

 - **Eager Loading by Default**: Settings load eagerly on import; enable lazy loading with `PYTTING_LAZY_LOAD`.

## Installation

```bash
pip install pyttings
```

## Quick Start

1. **Define Your Settings Module** (`myapp/settings.py`):

```python
DEBUG: bool = True
OTHER_BOOLEAN = True  # Type hint is not required but recommended
DATABASE_URL: str = "sqlite:///db.sqlite3"
PORT: int = 8000
SOME_LIST: list[str] = ["a", "b", "c"]
SOME_DICT: dict[str, str] = {"a": "b", "c": "d"}
SOME_SET: set[str] = {"a", "b", "c"}
SOME_UNION_TYPE: dict | str = "some_str"
```

2. **Set the Settings Module**:

```bash
export PYTTING_SETTINGS_MODULE="myapp.settings"
```

3. **Use Pyttings**:

```python
from pyttings import settings

print(settings.DEBUG)  # Output: True
print(settings.DATABASE_URL)  # Output: sqlite:///db.sqlite3
print(settings.PORT)  # Output: 8000
print(settings.SOME_LIST)  # Output: ['a', 'b', 'c']
```

## Configuration

### Required: `PYTTING_SETTINGS_MODULE`

Specify the settings module using the `PYTTING_SETTINGS_MODULE` environment variable. This is mandatory for Pyttings to know where to load your settings from.

```bash
export PYTTING_SETTINGS_MODULE="myapp.settings"
```

### Optional: `PYTTING_ENV_PREFIX`

By default, Pyttings uses `PYTTING_` as the prefix for environment variables. For example, to override the `DEBUG` setting, you would set:

```bash
export PYTTING_DEBUG="False"
```

If you want to use a custom prefix (e.g., `MYAPP_`), set the `PYTTING_ENV_PREFIX` environment variable:

```bash
export PYTTING_ENV_PREFIX="MYAPP_"
export MYAPP_DEBUG="False"
```

Now, Pyttings will look for `MYAPP_DEBUG` instead of `PYTTING_DEBUG`.

### Optional: `PYTTING_CUSTOM_CLASS_METHOD_NAME`

You can change the method name used for custom class parsing. By default, Pyttings looks for `__pyttings_convert__`. To use a custom method name, set:

```bash
export PYTTING_CUSTOM_CLASS_METHOD_NAME="custom_method_name"
```

### Optional: `PYTTING_LAZY_LOAD`

By default, Pyttings loads settings eagerly at import time, surfacing misconfigurations early. If you prefer to enable lazy loading so settings are only evaluated when accessed, set:

```bash
export PYTTING_LAZY_LOAD="True"
```

## Advanced Features

### Automatic Type Parsing

Pyttings automatically converts environment variables to match the expected type based on the settings module.

```python
# myapp/settings.py
DEBUG: bool = True
PORT: int = 8000
```

```bash
export PYTTING_DEBUG="False"
export PYTTING_PORT="8080"
```

Pyttings will automatically convert `PYTTING_DEBUG` to `False` (boolean) and `PYTTING_PORT` to `8080` (integer), ensuring type consistency.

### Union Type Support

If a setting is defined with a union type hint, Pyttings will try each type until a valid conversion is found.

```python
SOME_UNION_TYPE: dict | str = "some_str"
```

```bash
export PYTTING_SOME_UNION_TYPE='{"key": "value"}'
```

Pyttings will first attempt to convert the value to a `dict`, succeeding if valid, or fallback to `str`.

### Literal Type Support

If a setting is defined with a `Literal` type hint, Pyttings only accepts the listed values and converts them to the literal's type. This works for both strings and integers (and mixed literals):

```python
from typing import Literal

LOG_LEVEL: Literal["debug", "info", "warning"] = "info"
RETRIES: Literal[1, 2, 3] = 1
MIXED: Literal["1", 2] = "1"
```

```bash
export PYTTING_LOG_LEVEL="warning"  # -> "warning"
export PYTTING_RETRIES="3"          # -> 3
export PYTTING_MIXED="2"            # -> 2 (int)
```

A value outside the allowed literals raises `SettingMisconfigured`. Literals also work inside unions and collection types, such as `list[Literal["a", "b"]]`.

### Collection Type Validation

Pyttings ensures that lists, tuples, sets, and dictionaries maintain correct element types.

```python
ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1"]
```

```bash
export PYTTING_ALLOWED_HOSTS='["example.com", "api.example.com"]'
```

Pyttings will correctly parse `PYTTING_ALLOWED_HOSTS` as a `list[str]`.

### Custom Class Parsers

You can define custom classes that implement a conversion method (default: `__pyttings_convert__`, configurable via `PYTTING_CUSTOM_CLASS_METHOD_NAME`).

#### Example

```python
class MultipleArgsCustomClass:
    def __init__(self, int_value: int, str_value: str, value: int | str):
        self.int_value = int_value
        self.str_value = str_value
        self.value = value

    @classmethod
    def __pyttings_convert__(
        cls, value: dict[str, int | str]
    ) -> "MultipleArgsCustomClass":
        return cls(
            int_value=value["int_value"],
            str_value=value["str_value"],
            value=value["value"],
        )
```

```python
# myapp/settings.py
...
SOME_MULTIPLE_CUSTOM_CLASS: MultipleArgsCustomClass = MultipleArgsCustomClass(1, "2", 3)
```

```bash
export PYTTING_SOME_MULTIPLE_CUSTOM_CLASS='{"int_value": 3, "str_value": "2", "value": "1"}'
```

Pyttings will correctly parse the value into an instance of `MultipleArgsCustomClass` using the `__pyttings_convert__` method.

## Strict Type Enforcement & `SettingMisconfigured`

If Pyttings cannot parse a setting into its expected type, it raises `SettingMisconfigured`. This ensures settings are always correctly configured and prevents unexpected behavior.

For example:

```python
ALLOWED_HOSTS: list[str] = ["localhost"]
SOME_STRICT_LIST: list[str] = ["localhost"]
```

```bash
export PYTTING_ALLOWED_HOSTS="123"
export PYTTING_SOME_STRICT_LIST=[1,2,3]
```

Since `123` is not a valid list and `[1,2,3]` is not a valid `list[str]`, Pyttings will raise:

```
SettingMisconfigured: Invalid type for ALLOWED_HOSTS with configured value '123'.
Expected list[str].

SettingMisconfigured: Invalid type for SOME_STRICT_LIST with configured value '[1,2,3]'.
Expected list[str].
```

Similarly, if a custom class method does not meet the required signature (single argument with a type hint), Pyttings will raise an error.

## Overriding Settings in Tests

Use `override_settings` to temporarily replace setting values in tests. It works as a context manager and as a function or class decorator, restores the previous values even if the test raises, supports nested overrides, and takes precedence over environment variables.

```python
from pyttings import override_settings, settings

@override_settings(DEBUG=False, PORT=9000)
def test_api_uses_test_config():
    assert settings.DEBUG is False
    assert settings.PORT == 9000


def test_with_context_manager():
    with override_settings(PORT=9000):
        assert settings.PORT == 9000
```

Class decorators wrap methods whose names start with `test` and common setup/teardown methods (`setUp`, `tearDown`, `setup_method`, `teardown_method`, `asyncSetUp`, `asyncTearDown`). Class-level fixtures are not wrapped. Async test functions are supported.

Overrides are applied to the shared settings cache and are not written to `os.environ`, so they are not thread-safe. Unknown setting names are added temporarily and restored or removed when the override exits. Any `Settings` instance also provides the same mechanism through its `.override(...)` method.

## Static Typing & IDE Navigation

`settings` is resolved dynamically, so by default type checkers see every setting as `Any` and "go to definition" (Ctrl/Cmd+click) has nowhere to go. To keep the types from your settings module and jump straight to it, create a small typed entry point in your project:

```python
# myapp/conf.py
import myapp.settings
from pyttings import typed_settings

settings = typed_settings(myapp.settings)
```

```python
from myapp.conf import settings

settings.LOG_LEVEL  # Type checker sees `str`; Ctrl+click opens myapp/settings.py
```

At runtime, `typed_settings` returns the regular pyttings `settings` object, so environment variable overrides still apply. The module you pass is normally the one in `PYTTING_SETTINGS_MODULE`, but it doesn't have to be. For example, tests can point `PYTTING_SETTINGS_MODULE` at a separate test settings module. `typed_settings` raises `ValueError` only if the module declares a setting that the loaded settings module doesn't have.

> **Tips**
> - Annotate your settings (`LOG_LEVEL: str = "INFO"`). Without an annotation, pyright infers a literal type such as `Literal[8000]` instead of `int`.
> - `typed_settings` works with pyright, basedpyright and Pylance. mypy does not keep a module's type through a function call. For mypy, use a `TYPE_CHECKING` import instead:
>
>   ```python
>   # myapp/conf.py
>   from typing import TYPE_CHECKING
>
>   if TYPE_CHECKING:
>       from myapp import settings as settings
>   else:
>       from pyttings import settings as settings
>   ```

## Contributing

Contributions are welcome! If you'd like to contribute to Pyttings, please follow these steps:

1. Fork the repository on [GitHub](https://github.com/ruitcatarino/pyttings).
2. Create a new branch for your feature or bugfix.
3. Make your changes and ensure tests pass.
4. Submit a pull request with a clear description of your changes.

Please ensure your code follows the project's style and includes appropriate tests. See the `Makefile`.

---

## License

Pyttings is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
