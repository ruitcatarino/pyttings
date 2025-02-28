import os

from .core import Settings

settings = Settings(lazy_load=os.getenv("PYTTING_LAZY_LOAD", "False").lower() == "true")

__all__ = ["settings"]
