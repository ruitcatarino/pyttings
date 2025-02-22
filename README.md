# Pyttings
Lightweight Python settings management with namespacing and modular files. Inspired by Django.

## Features

- **Namespaced Settings**: Use a prefix (e.g., `PYTTING_`) to avoid conflicts.
- **Custom Prefix**: Change the prefix using `PYTTING_ENV_PREFIX`.
- **Modular Settings**: Load settings from a module with `PYTTING_SETTINGS_MODULE`.
- **Environment Variables**: Override settings easily, with automatic type parsing.
- **Type Hint Support**: Converts environment variables to the expected type.
- **Union Type Support**: Supports multiple possible types for a setting.
- **Collection Type Validation**: Ensures list, tuple, set, and dict elements match expected types.

## Installation

```bash
pip install pyttings
```

## Quick Start

1. **Define Your Settings Module** (`myapp/settings.py`), we recommend the use of type hints but they are optional:
```python
DEBUG: bool = True
OTHER_BOOLEAN = True
DATABASE_URL: str = "sqlite:///db.sqlite3"
SECRET_KEY = "my-secret-key"
PORT: int = 8000
OTHER_INT = 1
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
print(settings.OTHER_BOOLEAN)  # Output: True
print(settings.DATABASE_URL)  # Output: sqlite:///db.sqlite3
print(settings.SECRET_KEY)  # Output: my-secret-key
print(settings.PORT)  # Output: 8000
print(settings.OTHER_INT)  # Output: 1
print(settings.SOME_LIST)  # Output: ['a', 'b', 'c']
print(settings.SOME_DICT)  # Output: {'a': 'b', 'c': 'd'}
print(settings.SOME_SET)  # Output: {'a', 'b', 'c'}
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

## Advanced Features

### Automatic Type Parsing

Pyttings automatically converts environment variables to match the expected type hint or type based on the settings module.
```python
# myapp/settings.py
DEBUG: bool = True
OTHER_BOOLEAN = True # type hint is not required but recommended
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

### Collection Type Validation

Pyttings ensures that lists, tuples, sets, and dictionaries maintain correct element types.
```python
ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1"]
```
```bash
export PYTTING_ALLOWED_HOSTS='["example.com", "api.example.com"]'
```
Pyttings will correctly parse `PYTTING_ALLOWED_HOSTS` as a `list[str]`.

### Handling Misconfigured Settings

If Pyttings cannot convert a value to the expected type, it raises a `SettingMisconfigured` exception. This helps catch misconfigured settings early.
```python
PORT: int = 8000
```
```bash
export PYTTING_PORT="not_an_int"
```
When attempting to access `settings.PORT`, Pyttings will raise:
```
SettingMisconfigured: Invalid type for PORT with configured value 'not_an_int'.
Expected <class 'int'>.
```
This ensures that your application fails fast if an invalid configuration is provided.

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

