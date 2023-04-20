# Inital code taken from https://github.com/boringcactus/Appel-Jacobson-scrabble/blob/canon/board.py

import copy
import itertools as it

from dataclasses import dataclass
from enum import IntEnum


class Direction(IntEnum):
    ACROSS = 1
    DOWN = 2


@dataclass(frozen=True, order=True)
class Position():
    dir: Direction
    row: int
    col: int


class Board:
    def __init__(self):
        self.size = 15
        self._tiles = [['.'] * self.size for i in range(self.size)]

    def __str__(self):
        return '\n'.join(''.join(x if x != '.' else '_' for x in row) for row in self._tiles)

    def all_positions(self):
        return it.product(range(0, self.size), range(0, self.size))

    def tile(self, pos):
        row, col = pos
        return self._tiles[row][col]

    def set_tile(self, pos, tile):
        row, col = pos
        self._tiles[row][col] = tile

    def in_bounds(self, pos):
        row, col = pos
        return row >= 0 and row < self.size and col >= 0 and col < self.size

    def is_empty(self, pos):
        return self.in_bounds(pos) and self.tile(pos) == '.'

    def is_filled(self, pos):
        return self.in_bounds(pos) and self.tile(pos) != '.'

    def is_first_turn(self):
        return all('.' == c for c in it.chain(*self._tiles))

    def copy(self):
        return copy.deepcopy(self)
