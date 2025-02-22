# tests/settings.py

# Type hinted settings
NONE_VALUE: None = None
DEBUG: bool = True
ENABLE_FEATURE: bool = False
PORT: int = 8000
DATABASE_URL: str = "sqlite:///db.sqlite3"
SECRET_KEY: str = "my-secret-key"
SOME_DICT: dict = {"a": "b", "c": "d"}
SOME_LIST: list = ["a", "b", "c"]
SOME_TUPLE: tuple = ("a", "b", "c")
SOME_SET: set = {"a", "b", "c"}
SOME_UNION_TYPE: dict | str = "some_str"

# Strict type hinted settings
SOME_STRICT_DICT: dict[str, str] = {"a": "b", "c": "d"}
SOME_STRICT_LIST: list[str] = ["a", "b", "c"]


# Type hintless settings
NO_TYPE_HINT_NONE = None
NO_TYPE_HINT_BOOL = True
NO_TYPE_HINT_INT = 1
NO_TYPE_HINT_FLOAT = 1.0
NO_TYPE_HINT_STR = "a"
NO_TYPE_HINT_DICT = {"a": "b", "c": "d"}
NO_TYPE_HINT_LIST = ["a", "b", "c"]
NO_TYPE_HINT_TUPLE = ("a", "b", "c")
NO_TYPE_HINT_SET = {"a", "b", "c"}
