from dataclasses import dataclass
from typing import Any


@dataclass(frozen = True)
class Color:
    r: float
    g: float
    b: float
    a: float = 1.0

    def __add__(self, other):
        if not isinstance(other, Color):
            raise TypeError()

        return Color(
            self.r + other.r,
            self.g + other.g,
            self.b + other.b,
            self.a + other.a,
        )

    def __mul__(self, other):
        if isinstance(other, Color):
            return Color(
                self.r * other.r,
                self.g * other.g,
                self.b * other.b,
                self.a + other.a,
            )
        else:
            return Color(
                self.r * other,
                self.g * other,
                self.b * other,
                self.a * other,
            )

    @classmethod
    def mix(first, second, amount):
        return Color(
            first.r * (1.0 - amount) + second.r * amount,
            first.g * (1.0 - amount) + second.g * amount,
            first.b * (1.0 - amount) + second.b * amount,
            first.a * (1.0 - amount) + second.a * amount,
        )


@dataclass(frozen = True)
class ParameterModifier:
    parameter: str
    value: Any
    operation: str = "add"
