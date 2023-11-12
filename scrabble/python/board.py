# Inital code taken from https://github.com/boringcactus/Appel-Jacobson-scrabble/blob/canon/board.py

import copy
import itertools as it
from dataclasses import dataclass
from enum import IntEnum

Letter= str # synonym for str, but make it clear that it's a letter

CellCoord = tuple[int, int]


class Direction(IntEnum):
    ACROSS = 1
    DOWN = 2


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
        return row >= 0 and row < self.size and col >= 0 and col < self.size

    def is_empty(self, pos: CellCoord) -> bool:
        return self.in_bounds(pos) and self.tile(pos) == "."

    def is_filled(self, pos: CellCoord) -> bool:
        return self.in_bounds(pos) and self.tile(pos) != "."

    def is_first_turn(self) -> bool:
        return all("." == c for c in it.chain(*self._tiles))

    def copy(self) -> "Board":  # This is a recursive type annotation, actually a limitation of mypy
        return copy.deepcopy(self)
