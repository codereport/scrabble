"""
Scrabble Game

Started from https://arcade.academy/examples/array_backed_grid.html#array-backed-grid
"""

import arcade
import random           # shuffle
import itertools as it  # permutations
import numpy     as np  # transpose

from result import Ok, Err
from enum   import Enum

## Constants

ROW_COUNT    = 15
COLUMN_COUNT = 15
WIDTH        = 50  # Grid width
HEIGHT       = 50  # Grid height
MARGIN       = 5   # This sets the margin between each cell and on the edges of the screen.

BOTTOM_MARGIN = 100
RIGHT_MARGIN  = 400

SCREEN_WIDTH  = (WIDTH + MARGIN)  * COLUMN_COUNT + MARGIN + RIGHT_MARGIN
SCREEN_HEIGHT = (HEIGHT + MARGIN) * ROW_COUNT    + MARGIN + BOTTOM_MARGIN
SCREEN_TITLE  = "Scrabble"

#TODO convert to Enum
NO = 1
DL = 2
DW = 3
TL = 4
TW = 5

BOARD = [[TW, NO, NO, DL, NO, NO, NO, TW, NO, NO, NO, DL, NO, NO, TW],
         [NO, DW, NO, NO, NO, TL, NO, NO, NO, TL, NO, NO, NO, DW, NO],
         [NO, NO, DW, NO, NO, NO, DL, NO, DL, NO, NO, NO, DW, NO, NO],
         [DL, NO, NO, DW, NO, NO, NO, DL, NO, NO, NO, DW, NO, NO, DL],
         [NO, NO, NO, NO, DW, NO, NO, NO, NO, NO, DW, NO, NO, NO, NO],
         [NO, TL, NO, NO, NO, TL, NO, NO, NO, TL, NO, NO, NO, TL, NO],
         [NO, NO, DL, NO, NO, NO, DL, NO, DL, NO, NO, NO, NO, DL, NO],
         [TW, NO, NO, DL, NO, NO, NO, DW, NO, NO, NO, DL, NO, NO, TW],
         [NO, NO, DL, NO, NO, NO, DL, NO, DL, NO, NO, NO, NO, DL, NO],
         [NO, TL, NO, NO, NO, TL, NO, NO, NO, TL, NO, NO, NO, TL, NO],
         [NO, NO, NO, NO, DW, NO, NO, NO, NO, NO, DW, NO, NO, NO, NO],
         [DL, NO, NO, DW, NO, NO, NO, DL, NO, NO, NO, DW, NO, NO, DL],
         [NO, NO, DW, NO, NO, NO, DL, NO, DL, NO, NO, NO, DW, NO, NO],
         [NO, DW, NO, NO, NO, TL, NO, NO, NO, TL, NO, NO, NO, DW, NO],
         [TW, NO, NO, DL, NO, NO, NO, TW, NO, NO, NO, DL, NO, NO, TW]]

TILE_SCORE = {
    'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2,  'H': 4, 'I': 1, 'J': 8,
    'K': 5, 'L': 1, 'M': 3, 'N': 1, 'O': 1, 'P': 3, 'Q': 10, 'R': 1, 'S': 1, 'T': 1,
    'U': 1, 'V': 4, 'W': 4, 'X': 8, 'Y': 4, 'Z': 10}

TILE_BAG = \
    ['A'] * 9 + ['B'] * 2 + ['C'] * 2 + ['D'] * 4 + ['E'] * 12 + ['F'] * 2 + ['G'] * 3 + \
    ['H'] * 2 + ['I'] * 9 + ['J'] * 1 + ['K'] * 1  + ['L'] * 4 + ['M'] * 2 + ['N'] * 6 + \
    ['O'] * 8 + ['P'] * 2 + ['Q'] * 1 + ['R'] * 6  + ['S'] * 4 + ['T'] * 6 + ['U'] * 4 + \
    ['V'] * 2 + ['W'] * 2 + ['X'] * 1 + ['Y'] * 2  + ['Z'] * 1

COLOR_NORMAL        = (200, 196, 172)
COLOR_TRIPLE_WORD   = (241, 108,  77)
COLOR_TRIPLE_LETTER = ( 58, 156, 184)
COLOR_DOUBLE_WORD   = (250, 187, 170)
COLOR_DOUBLE_LETTER = (189, 215, 214)


## Enumerators

class Direction(Enum):
    ACROSS = 1
    DOWN = 2


## Free functions

def letter_multiplier(row, col):
    if BOARD[row][col] == DL: return 2
    if BOARD[row][col] == TL: return 3
    return 1


def word_multiplier(row, col):
    if BOARD[row][col] == DW: return 2
    if BOARD[row][col] == TW: return 3
    return 1


def tile_color(row, col):
    if BOARD[row][col] == DL: return COLOR_DOUBLE_LETTER
    if BOARD[row][col] == DW: return COLOR_DOUBLE_WORD
    if BOARD[row][col] == TL: return COLOR_TRIPLE_LETTER
    if BOARD[row][col] == TW: return COLOR_TRIPLE_WORD
    return COLOR_NORMAL

def prefix_tiles(board, dir, row, col):
    row_delta = 1 if dir == Direction.DOWN else 0
    col_delta = 0 if dir == Direction.DOWN else 1
    prev_row, prev_col, prefix_tiles = row, col, ''
    while prev_row - row_delta >= 0 and prev_col - col_delta >= 0:
        prev_row -= row_delta
        prev_col -= col_delta
        if board[prev_row][prev_col] != '.':
            prefix_tiles += board[prev_row][prev_col]
        else:
            break
    return prefix_tiles[::-1]

def word_score(board, dictionary, dir, letters, row, col):
    if board[row][col] != '.':
        return Err('cannot start word on existing tile')
    if dir == Direction.ACROSS:
        if len([1 for c in board[row][col:] if c != '.']) < len(letters):
            return Err('outside of board')
    else:
        if len([1 for c in np.transpose(board)[col][row:] if c == '.']) < len(letters):
            return Err('outside of board')

    # currently only support crossword style #TODO support adjacent
    word_played = prefix_tiles(board, dir, row, col) # TODO currently aren't included in score
    score       = 0
    word_mult   = 1
    row_delta   = 1 if dir == Direction.DOWN else 0
    col_delta   = 0 if dir == Direction.DOWN else 1
    crosses     = True if len(word_played) else False

    for letter in letters:
        while board[row][col] != '.':
            word_played = word_played + board[row][col]
            score += TILE_SCORE.get(board[row][col])
            row += row_delta
            col += col_delta
            crosses = True
        word_played = word_played + letter
        score += TILE_SCORE.get(letter) * letter_multiplier(row, col)
        word_mult *= word_multiplier(row, col)
        row += row_delta
        col += col_delta

    score *= word_mult
    score += 50 if len(letters) == 7 else 0

    if not crosses:
        return Err('does not overlap with any other word')

    if word_played not in dictionary:
        return Err(word_played + ' not in dictionary')

    # TODO return score
    return Ok((score, word_played))



class MyGame(arcade.Window):
    """Main application class"""

    def __init__(self, width, height, title):
        """Set up the application"""

        super().__init__(width, height, title)

        # Create a 2 dimensional array. A two dimensional array is simply a list of lists.
        self.grid = [['.'] * 15 for i in range(15)]
        self.grid[7][3] = 'H'
        self.grid[7][4] = 'E'
        self.grid[7][5] = 'L'
        self.grid[7][6] = 'L'
        self.grid[7][7] = 'O'

        arcade.set_background_color(arcade.color.BLACK)

        # Cursor for typings
        self.cursor   = 0  # 0 = off, 1 = across, 2 = down
        self.cursor_x = 0
        self.cursor_y = 0

        # Setup game
        random.shuffle(TILE_BAG)
        tile_bag_index = 0

        self.your_tiles      = TILE_BAG[0: 7]
        self.oppenents_tiles = TILE_BAG[7: 14]

        self.DICTIONARY = set()
        with open('dictionary.txt') as f:
            for line in f:
                self.DICTIONARY.add(line.strip())

        self.letters_typed = {}

        # visual verification
        # print(sum((len(list(it.permutations(self.your_tiles, i)))         for i in range(7, 1, -1))))
        # print(sum((len(list(it.permutations(self.your_tiles + ['A'], i))) for i in range(8, 1, -1))))

        words = {''.join(p) for i in range(4, 1, -1) for p in it.permutations(self.your_tiles, i)}  # if ''.join(p) in self.DICTIONARY}

        # hack to generate words
        plays = []
        for row in range(ROW_COUNT):
            for col in range(COLUMN_COUNT):
                for word in words:
                    score = word_score(self.grid, self.DICTIONARY, Direction.DOWN, word, row, col)
                    if score.is_ok():
                        plays.append(score.unwrap())

        for play in sorted(plays):
            print(play)

    def on_draw(self):
        """Render the screen"""

        arcade.start_render()

        self.dir = Direction.ACROSS if self.cursor == 1 else Direction.DOWN
        if len(self.letters_typed):
            start_row, start_col = next(iter(self.letters_typed))
            valid_word = len(self.letters_typed) and \
                word_score(self.grid,
                           self.DICTIONARY,
                           self.dir,
                           ''.join(self.letters_typed.values()),
                           14 - start_row, # super hacky
                           start_col).is_ok()
        else:
            valid_word = False

        played_tile_color = arcade.color.DARK_PASTEL_GREEN if valid_word else arcade.color.SAE

        # Draw the grid
        for row in range(ROW_COUNT):
            for column in range(COLUMN_COUNT):
                color = tile_color(row, column) if self.grid[row][column] == '.' else arcade.color.AMETHYST
                if (row, column) in self.letters_typed:
                    color = played_tile_color

                x = (MARGIN + WIDTH)  * column + MARGIN + WIDTH  // 2
                y = (MARGIN + HEIGHT) * row    + MARGIN + HEIGHT // 2 + BOTTOM_MARGIN
                arcade.draw_rectangle_filled(x, y, WIDTH, HEIGHT, color)

                if self.grid[row][column] != '.':
                    arcade.draw_text(self.grid[row][column], x-15, y-25, arcade.color.WHITE, 40, bold=True)
                elif (row, column) in self.letters_typed:
                    arcade.draw_text(self.letters_typed.get((row, column)), x-15, y-25, arcade.color.WHITE, 40, bold=True)

        # Draw cursor
        if self.cursor and len(self.letters_typed) == 0:
            color = arcade.color.WHITE if self.cursor == 1 else arcade.color.BLACK
            x = (MARGIN + WIDTH)  * self.cursor_x + MARGIN + WIDTH  // 2
            y = (MARGIN + HEIGHT) * self.cursor_y + MARGIN + HEIGHT // 2 + BOTTOM_MARGIN
            arcade.draw_rectangle_filled(x, y, WIDTH, HEIGHT, color)

        # Draw tiles
        tiles_left = list(self.letters_typed.values())
        for i, tile in enumerate(self.your_tiles):
            if tile in tiles_left:
                color = played_tile_color
                tiles_left.remove(tile)
            else:
                color = arcade.color.AMETHYST
            x = (4 + i) * (MARGIN + WIDTH) + MARGIN + WIDTH // 2
            y = 50

            # Draw the box - TODO refactor this into draw_tile
            arcade.draw_rectangle_filled(x, y, WIDTH, HEIGHT, color)
            arcade.draw_text(tile, x-15, y-25, arcade.color.WHITE, 40, bold=True)

    def on_mouse_press(self, x, y, button, modifiers):
        """Called when the user presses a mouse button"""

        # Change the x/y screen coordinates to grid coordinates
        column = int(x // (WIDTH + MARGIN))
        row    = int((y - BOTTOM_MARGIN) // (HEIGHT + MARGIN))

        self.cursor_x = column
        self.cursor_y = row
        self.cursor   = (self.cursor + 1) % 3

        print(f"Click coordinates: ({x}, {y}). Grid coordinates: ({row}, {column})")

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key"""

        if str(chr(key)).isalpha():
            letter = chr(key - 32)
            print(letter)
            if letter in self.your_tiles:
                self.letters_typed[(self.cursor_y, self.cursor_x)] = letter
                if self.cursor == 1: self.cursor_x += 1
                if self.cursor == 2: self.cursor_y -= 1
                while self.grid[self.cursor_y][self.cursor_x] != '.':
                    if self.cursor == 1: self.cursor_x += 1
                    if self.cursor == 2: self.cursor_y -= 1

        if key == arcade.key.ESCAPE:
            self.letters_typed.clear()
            self.cursor = 0

        if key == arcade.key.BACKSPACE:
            if len(self.letters_typed):
                self.letters_typed.popitem()
                if self.cursor == 1: self.cursor_x -= 1
                if self.cursor == 2: self.cursor_y += 1
                while self.grid[self.cursor_y][self.cursor_x] != '.':
                    if self.cursor == 1: self.cursor_x -= 1
                    if self.cursor == 2: self.cursor_y += 1


def main():

    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
