# Inital code taken from https://github.com/boringcactus/Appel-Jacobson-scrabble/blob/canon/board.py

from __future__ import annotations

import copy
import itertools as it
from dataclasses import dataclass
from enum import Enum
from typing import SupportsIndex, TypeVar, overload

from typing_extensions import Self

Letter= str # synonym for str, but make it clear that it's a letter

CellCoord = tuple[int, int]

_T = TypeVar("_T")

class Vector(tuple[int, ...]):
    def __new__(cls, arg=(), *rest):
        return super().__new__(cls, (arg, *rest) if rest else arg)

    @property
    def zero(self) -> Self:
        "the zero vector with same dimensionality"
        return self.__class__(len(self) * (0,))

    def __repr__(self) -> str:
        return f"<Vector {super().__repr__()}>"

    def __bool__(self) -> bool:
        return any(self)

    def __mul__(self, scalar: SupportsIndex) -> Vector:
        # returning Vector() not self.__class__() because self might be a Direction
        # and Direction is very narrow type
        return Vector(scalar.__index__() * c for c in self)

    __rmul__ = __mul__

    def __neg__(self) -> Vector:
        return -1 * self

    @overload
    def __add__(self, other: tuple[int, ...]) -> Vector: ...

    @overload
    def __add__(self, other: tuple[_T, ...]) -> Vector: ...

    def __add__(self, other):
        return Vector(an + bn for an, bn in zip(self, other))

    __radd__ = __add__


class Direction(Vector, Enum):
    NONE = Vector(0, 0)
    DOWN = Vector(0, -1)
    ACROSS = Vector(1, 0)


@dataclass(frozen=True, order=True)
class Position:
    dir: Direction
    row: int
    col: int


class Board:
    size: int
    _tiles: list[list[Letter]]

    def __init__(self) -> None:
        self.size = 15
        self._tiles = [["."] * self.size for i in range(self.size)]

    def __str__(self) -> str:
        return "\n".join("".join(x if x != "." else "_" for x in row) for row in self._tiles)

    def all_positions(self) -> list[CellCoord]:
        return list(it.product(range(0, self.size), range(0, self.size)))

    def tile(self, pos: CellCoord) -> Letter:
        row, col = pos
        return self._tiles[row][col]

    def set_tile(self, pos: CellCoord, tile: Letter) -> None:
        row, col = pos
        self._tiles[row][col] = tile

    def in_bounds(self, pos: CellCoord) -> bool:
        row, col = pos
        return 0 <= row < self.size and 0 <= col < self.size

    def is_empty(self, pos: CellCoord) -> bool:
        return self.in_bounds(pos) and self.tile(pos) == "."

    def is_filled(self, pos: CellCoord) -> bool:
        return self.in_bounds(pos) and self.tile(pos) != "."

    def is_first_turn(self) -> bool:
        return all("." == c for c in it.chain(*self._tiles))

    def copy(self) -> Self:
        return copy.deepcopy(self)
