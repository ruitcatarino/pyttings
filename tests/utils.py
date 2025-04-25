from typing import List


class ListOfInts:
    def __init__(self, value: list[int]):
        self.value = value

    @classmethod
    def __pyttings_convert__(cls, value: list[int]) -> "ListOfInts":
        return cls(value)

    def __eq__(self, other):
        return self.value == other.value


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
            int_value=value["int_value"],  # type: ignore
            str_value=value["str_value"],  # type: ignore
            value=value["value"],
        )

    def __eq__(self, other):
        return (
            self.int_value == other.int_value
            and self.str_value == other.str_value
            and self.value == other.value
        )


class SimpleCustomClass:
    def __init__(self, value):
        self.value = value

    @classmethod
    def __pyttings_convert__(cls, value: List[int]):
        return cls(value)

    def __eq__(self, other):
        return self.value == other.value


class InvalidCustomClass:
    # Missing parameter
    @classmethod
    def __pyttings_convert__(cls): ...


class UntypedCustomClass:
    # Missing type hint
    @classmethod
    def __pyttings_convert__(cls, value): ...

    def __init__(self, value): ...
