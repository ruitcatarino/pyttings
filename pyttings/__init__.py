import os

from pyttings.type_converter import parse_bool

from .core import Settings

settings = Settings(lazy_load=parse_bool(os.getenv("PYTTING_LAZY_LOAD", "False")))

__all__ = ["settings"]
