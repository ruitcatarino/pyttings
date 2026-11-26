from __future__ import annotations


class PostponedListOfInts:
    def __init__(self, value: list[int]):
        self.value = value

    @classmethod
    def __pyttings_convert__(cls, value: list[int]) -> PostponedListOfInts:
        return cls(value)

    def __eq__(self, other):
        return self.value == other.value
