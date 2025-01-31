# Pyttings
Lightweight Python settings management with namespacing and modular files. Inspired by Django.

## Features

- **Namespaced Settings**: Use a prefix (e.g., `PYTTING_`) to avoid conflicts.
- **Custom Prefix**: Change the prefix using `PYTTING_ENV_PREFIX`.
- **Modular Settings**: Load settings from a module with `PYTTING_SETTINGS_MODULE`.
- **Environment Variables**: Override settings easily.

## Installation

```bash
pip install pyttings
```

## Quick Start

1. **Define Your Settings Module** (`myapp/settings.py`):
```python
DEBUG = True
DATABASE_URL = "sqlite:///db.sqlite3"
SECRET_KEY = "my-secret-key"
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

## Contributing

Contributions are welcome! If you'd like to contribute to Pyttings, please follow these steps:

1. Fork the repository on [GitHub](https://github.com/ruitcatarino/pyttings).
2. Create a new branch for your feature or bugfix.
3. Make your changes and ensure tests pass.
4. Submit a pull request with a clear description of your changes.

Please ensure your code follows the project's style and includes appropriate tests.

---

## License

Pyttings is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
