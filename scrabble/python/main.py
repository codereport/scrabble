"""
Scrabble Game

Started from https://arcade.academy/examples/array_backed_grid.html#array-backed-grid
"""

import arcade
import random                # shuffle
import copy                  # deepcopy
import itertools      as it  # permutations
import more_itertools as mt  # flatten
import numpy          as np  # transpose

from result      import Ok, Err
from enum        import Enum
from joblib      import Parallel, delayed
from collections import Counter, defaultdict

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

FONT_SIZE         = 30
HORIZ_TEXT_OFFSET = 13
VERT_TEXT_OFFSET  = 15

# TODO convert to Enum
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
         [NO, NO, DL, NO, NO, NO, DL, NO, DL, NO, NO, NO, DL, NO, NO],
         [TW, NO, NO, DL, NO, NO, NO, DW, NO, NO, NO, DL, NO, NO, TW],
         [NO, NO, DL, NO, NO, NO, DL, NO, DL, NO, NO, NO, DL, NO, NO],
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
    ['H'] * 2 + ['I'] * 9 + ['J'] * 1 + ['K'] * 1 + ['L'] * 4  + ['M'] * 2 + ['N'] * 6 + \
    ['O'] * 8 + ['P'] * 2 + ['Q'] * 1 + ['R'] * 6 + ['S'] * 4  + ['T'] * 6 + ['U'] * 4 + \
    ['V'] * 2 + ['W'] * 2 + ['X'] * 1 + ['Y'] * 2 + ['Z'] * 1

ARROW_KEYS = [arcade.key.LEFT, arcade.key.RIGHT, arcade.key.UP, arcade.key.DOWN]

COLOR_NORMAL        = (200, 196, 172)
COLOR_TRIPLE_WORD   = (241, 108,  77)
COLOR_TRIPLE_LETTER = ( 58, 156, 184)
COLOR_DOUBLE_WORD   = (250, 187, 170)
COLOR_DOUBLE_LETTER = (189, 215, 214)

## Enumerators & Helper Classes

class Direction(Enum):
    ACROSS = 1
    DOWN = 2

class Hooks(Enum):
    OFF     = 0
    ALL     = 1
    ON_RACK = 2

# TODO make immutable
class Position():
    def __init__(self, dir, row, col):
        self.row = row
        self.col = col
        self.dir = dir

    def __lt__(self, other):
        return self.row < other.row

    def __eq__(self, other):
        return self.row == other.row and \
               self.col == other.col and \
               self.dir == other.dir

    def __repr__(self):
        return str(self.tuple())

    def tuple(self):
        return (self.row, self.col, self.dir)

class Player():
    def __init__(self, tiles):
        self.tiles           = tiles
        self.score           = 0
        self.word_ranks      = []
        self.last_word_score = 0

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
    prev_row, prev_col, tiles, score = row, col, '', 0
    while prev_row - row_delta >= 0 and prev_col - col_delta >= 0:
        prev_row -= row_delta
        prev_col -= col_delta
        if board[prev_row][prev_col] != '.':
            tiles += board[prev_row][prev_col]
            score += TILE_SCORE.get(board[prev_row][prev_col])
        else:
            break
    return (tiles[::-1], score)

def suffix_tiles(board, dir, row, col):
    row_delta = 1 if dir == Direction.DOWN else 0
    col_delta = 0 if dir == Direction.DOWN else 1
    next_row, next_col, tiles, score = row, col, '', 0
    while next_row + row_delta < 15 and next_col + col_delta < 15:
        next_row += row_delta
        next_col += col_delta
        if board[next_row][next_col] != '.':
            tiles += board[next_row][next_col]
            score += TILE_SCORE.get(board[next_row][next_col])
        else:
            break
    return (tiles, score)

def is_first_turn(board):
    return all('.' == c for c in mt.flatten(board))

def word_score(board, dictionary, letters, pos, first_call, prefixes):
    dir, row, col = pos.dir, pos.row, pos.col
    row = 14 - row
    if board[row][col] != '.':
        return Err('cannot start word on existing tile')
    if dir == Direction.ACROSS:
        if len([1 for c in board[row][col:] if c == '.']) < len(letters):
            return Err('outside of board')
    else:
        if len([1 for c in np.transpose(board)[col][row:] if c == '.']) < len(letters):
            return Err('outside of board')

    word_played, score = prefix_tiles(board, dir, row, col)
    has_prefix         = len(word_played) > 0
    word_mult          = 1
    row_delta          = 1 if dir == Direction.DOWN else 0
    col_delta          = 0 if dir == Direction.DOWN else 1
    crosses            = True if len(word_played) else False
    valid_start        = False

    perpandicular_words = []

    for letter in letters:
        if word_played not in prefixes: return Err(word_played + ' prefix not in dictionary')
        while board[row][col] != '.':
            if word_played not in prefixes: return Err(word_played + ' prefix not in dictionary')
            word_played = word_played + board[row][col]
            score      += TILE_SCORE.get(board[row][col])
            row        += row_delta
            col        += col_delta
            crosses     = True
        if word_played not in prefixes: return Err(word_played + ' prefix not in dictionary')
        word_played = word_played + letter
        score += TILE_SCORE.get(letter) * letter_multiplier(row, col)
        if len(letters) == 1:
            one_letter_score = TILE_SCORE.get(letter) * letter_multiplier(row, col)
        word_mult *= word_multiplier(row, col)

        # find perpendicular words that need to be scored
        if dir == Direction.ACROSS:
            if (row + 1 <= 14 and board[row+1][col] != '.') or \
               (row - 1 >= 0  and board[row-1][col] != '.'):
                perpandicular_words.append((letter, (row, col)))
        else:
            if (col + 1 <= 14 and board[row][col+1] != '.') or \
               (col - 1 >= 0  and board[row][col-1] != '.'):
                perpandicular_words.append((letter, (row, col)))
        if row * col == 49:
            valid_start = True
        row += row_delta
        col += col_delta

    suffix, suffix_score = suffix_tiles(board, dir, row - row_delta, col - col_delta)
    word_played         += suffix
    has_suffix           = len(suffix) > 0

    score += suffix_score

    if not has_prefix and not has_suffix and len(letters) == 1:
        score -= one_letter_score

    score *= word_mult
    score += 50 if len(letters) == 7 else 0

    first_turn = is_first_turn(board)
    if not crosses and not len(suffix) and not len(perpandicular_words) and first_call:
        if first_turn:
            if not valid_start:
                return Err('first move must be through center tile')
        else:
            return Err('does not overlap with any other word')

    if first_call:
        opposite_dir = Direction.ACROSS if dir == Direction.DOWN else Direction.DOWN
        for word, (r, c) in perpandicular_words:
            new_pos = Position(opposite_dir, 14-r, c)
            res = word_score(board, dictionary, word, new_pos, False, prefixes)
            if res.is_ok():
                score += res.value[0]
                if len(word_played) == 1:
                    word_played = res.value[1]
            else:
                return res

    if word_played not in dictionary and not (len(word_played) == 1 and len(perpandicular_words)):
        return Err(word_played + ' not in dictionary')

    return Ok((score, word_played, pos))

def min_play_length(board, row, col, dir):
    if is_first_turn(board):
        return 1
    if dir == Direction.DOWN:
        if row - 1 >= 0 and board[row - 1][col] != '.':
            return 1
        for i in range(7):
            if row + i <= 14:
                if (col - 1     >= 0  and board[row + i][col - 1] != '.') or \
                   (col + 1     <= 14 and board[row + i][col + 1] != '.') or \
                   (row + 1 + i <= 14 and board[row + i + 1][col] != '.'):
                    return i + 1
    else:
        if col - 1 >= 0 and board[row][col - 1] != '.':
            return 1
        for i in range(7):
            if col + i <= 14:
                if (row - 1     >= 0  and board[row - 1][col + i] != '.') or \
                   (row + 1     <= 14 and board[row + 1][col + i] != '.') or \
                   (col + 1 + i <= 14 and board[row][col + i + 1] != '.'):
                    return i + 1
    return 10

def word_scores_for_row(board, dictionary, row, words, prefixes):
    plays = []
    if is_first_turn(board) and row != 7: return plays
    for col in range(COLUMN_COUNT):
        if board[14-row][col] == '.':
            # TODO duplication here
            if not is_first_turn(board):
                m = min_play_length(board, 14-row, col, Direction.DOWN)
                for word in words:
                    if len(word) >= m:
                        pos = Position(Direction.DOWN, row, col)
                        score = word_score(board, dictionary, word, pos, True, prefixes)
                        if score.is_ok():
                            plays.append(score.unwrap())
            m = min_play_length(board, 14-row, col, Direction.ACROSS)
            for word in words:
                if len(word) >= m:
                    pos = Position(Direction.ACROSS, row, col)
                    score = word_score(board, dictionary, word, pos, True, prefixes)
                    if score.is_ok():
                        plays.append(score.unwrap())
    return plays

class MyGame(arcade.Window):
    """Main application class"""

    def __init__(self, width, height, title):
        """Set up the application"""

        super().__init__(width, height, title)

        # Create a 2 dimensional array. A two dimensional array is simply a list of lists.
        self.grid        = [['.'] * 15 for i in range(15)]
        self.grid_backup = copy.deepcopy(self.grid)
        self.last_grid   = copy.deepcopy(self.grid)

        arcade.set_background_color(arcade.color.BLACK)

        # Cursor for typings
        self.cursor   = 0  # 0 = off, 1 = across, 2 = down
        self.cursor_x = 7
        self.cursor_y = 7

        # Setup game
        random.shuffle(TILE_BAG)
        self.tile_bag_index = 14

        self.player   = Player(TILE_BAG[0: 7])
        self.computer = Player(TILE_BAG[7:14])

        self.pause_for_analysis      = False
        self.pause_for_analysis_rank = None
        self.players_turn            = True
        self.player_plays            = []
        self.player_words_found      = set() # by rank
        self.player_scores_found     = set()

        self.hook_letters         = defaultdict(list)
        self.display_hook_letters = Hooks.OFF

        self.DICTIONARY = set()
        self.DEFINITIONS = dict()
        with open('../dictionary/nwl_2020.txt') as f:
            for line in f:
                words = line.strip().split()
                self.DICTIONARY.add(words[0])
                self.DEFINITIONS[words[0]] = ' '.join(words[1:])

        self.PREFIXES = set()
        self.PREFIXES.add('')
        for w in self.DICTIONARY:
            for i in range(1, len(w)+1):
                self.PREFIXES.add(w[:i])

        self.letters_typed        = {}
        self.letters_to_highlight = set()
        self.letters_bingoed      = set()
        self.definition           = ''

    def on_draw(self):
        """Render the screen"""

        arcade.start_render()

        played_tile_color = arcade.color.DARK_PASTEL_GREEN if self.is_playable() else arcade.color.SAE

        # Draw the grid
        for row in range(ROW_COUNT):
            render_row = 14 - row
            for column in range(COLUMN_COUNT):
                color = tile_color(row, column) if self.grid[render_row][column] == '.' else arcade.color.AMETHYST
                if (row, column) in self.letters_typed:
                    color = played_tile_color
                elif (row, column) in self.letters_to_highlight:
                    color = arcade.color.HOT_PINK

                x = (MARGIN + WIDTH)  * column + MARGIN + WIDTH  // 2
                y = (MARGIN + HEIGHT) * row    + MARGIN + HEIGHT // 2 + BOTTOM_MARGIN
                arcade.draw_rectangle_filled(x, y, WIDTH, HEIGHT, color)
                if (row, column) in self.letters_bingoed:
                    arcade.draw_rectangle_outline(x, y, WIDTH-4, HEIGHT-4, arcade.color.DARK_PASTEL_GREEN, 5)

                if self.grid[render_row][column] != '.':
                    arcade.draw_text(self.grid[render_row][column], x-HORIZ_TEXT_OFFSET, y-VERT_TEXT_OFFSET, arcade.color.WHITE, FONT_SIZE, bold=True, font_name='mono')
                elif (row, column) in self.letters_typed:
                    arcade.draw_text(self.letters_typed.get((row, column)), x-HORIZ_TEXT_OFFSET, y-VERT_TEXT_OFFSET, arcade.color.WHITE, FONT_SIZE, bold=True, font_name='mono')
                elif self.display_hook_letters != Hooks.OFF and not self.pause_for_analysis and (row, column) in self.hook_letters:
                    text_color = arcade.color.WHITE if color in [COLOR_TRIPLE_LETTER, COLOR_TRIPLE_WORD] else arcade.color.BLACK
                    letters = self.hook_letters[(row, column)]
                    xd, yd = 0, 0
                    for letter in letters:
                        arcade.draw_text(letter, x - WIDTH / 2.35 + xd, y + HEIGHT / 3.4 - yd, text_color, 10, bold=True, font_name='mono')
                        xd += 12
                        if xd == 48:
                            xd  = 0
                            yd += 11

        # Draw cursor
        if self.cursor and len(self.letters_typed) == 0:
            color = arcade.color.WHITE if self.cursor == 1 else arcade.color.BLACK
            x = (MARGIN + WIDTH)  * self.cursor_x + MARGIN + WIDTH  // 2
            y = (MARGIN + HEIGHT) * self.cursor_y + MARGIN + HEIGHT // 2 + BOTTOM_MARGIN
            arcade.draw_rectangle_filled(x, y, WIDTH, HEIGHT, color)

        # Draw blue score boxes (for player)
        column = 15
        row    = 14
        color  = COLOR_DOUBLE_LETTER
        x = (MARGIN + WIDTH)  * column + MARGIN * 2 + (WIDTH * 3.5)  // 2
        y = (MARGIN + HEIGHT) * row    + MARGIN + HEIGHT // 2 + BOTTOM_MARGIN
        arcade.draw_rectangle_filled(x, y, WIDTH * 3.5, HEIGHT, color)
        score = str(self.player.score) + " (" + str(self.player.last_word_score) + ")"
        arcade.draw_text(score, x-HORIZ_TEXT_OFFSET*4, y-VERT_TEXT_OFFSET*.75, arcade.color.BLACK, 20, bold=True, font_name='mono')

        # Draw pink score box (for computer)
        column = 15
        row    = 14
        color  = COLOR_DOUBLE_WORD
        x = (MARGIN + WIDTH)  * column + (MARGIN + (WIDTH * 3.5)) + MARGIN * 2 + (WIDTH * 3.5)  // 2
        y = (MARGIN + HEIGHT) * row    + MARGIN + HEIGHT // 2 + BOTTOM_MARGIN
        arcade.draw_rectangle_filled(x, y, WIDTH * 3.5, HEIGHT, color)
        score = str(self.computer.score) + " (" + str(self.computer.last_word_score) + ")"
        arcade.draw_text(score, x-HORIZ_TEXT_OFFSET*4, y-VERT_TEXT_OFFSET*.75, arcade.color.BLACK, 20, bold=True, font_name='mono')

        # Draw top word boxes
        for row in range(ROW_COUNT - 1):
            render_row = 14 - row # and place
            if len(self.player_plays) == 0 or render_row + 1 > len(self.player_plays):
                continue
            column = 15
            score, word, _ = self.player_plays[-render_row]
            if self.pause_for_analysis and self.pause_for_analysis_rank == render_row:
                color = arcade.color.HOT_PINK
            elif render_row in self.player_words_found:
                color = arcade.color.DARK_PASTEL_GREEN
            elif score in self.player_scores_found:
                color = arcade.color.YELLOW
            else:
                color = arcade.color.LIGHT_GRAY
            TOP_WORD_BOX_WIDTH = (MARGIN // 2 + (WIDTH * 3.5)) * 2
            x = (MARGIN + WIDTH)  * column + (2 * MARGIN) + TOP_WORD_BOX_WIDTH // 2
            y = (MARGIN + HEIGHT) * row    + MARGIN + HEIGHT // 2 + BOTTOM_MARGIN
            arcade.draw_rectangle_filled(x, y, TOP_WORD_BOX_WIDTH, HEIGHT, color)
            if render_row in self.player_words_found or self.pause_for_analysis:
                arcade.draw_rectangle_filled(x, y, TOP_WORD_BOX_WIDTH, HEIGHT, color)
                display = str(render_row) + ": " + word + " (" + str(score) + ")"
                arcade.draw_text(display, x-HORIZ_TEXT_OFFSET-130, y-VERT_TEXT_OFFSET*.75, arcade.color.BLACK, 20, bold=True, font_name='mono')

        # Draw tile rack
        tiles_left = list(self.letters_typed.values())
        for i, tile in enumerate(self.player.tiles):
            if tile in tiles_left:
                color = played_tile_color
                tiles_left.remove(tile)
            else:
                color = arcade.color.AMETHYST
            x = (4 + i) * (MARGIN + WIDTH) + MARGIN + WIDTH // 2
            y = 50

            # Draw the box - TODO refactor this into draw_tile
            arcade.draw_rectangle_filled(x, y, WIDTH, HEIGHT, color)
            arcade.draw_text(tile, x-HORIZ_TEXT_OFFSET, y-VERT_TEXT_OFFSET, arcade.color.WHITE, FONT_SIZE, bold=True, font_name='mono')

        # Draw word definition
        x = 12 * (MARGIN + WIDTH) + MARGIN + WIDTH // 2
        y = 50
        arcade.draw_text(self.definition, x-HORIZ_TEXT_OFFSET, y-VERT_TEXT_OFFSET, arcade.color.WHITE, 9, font_name='mono')

        # COMPUTER LOGIC
        if (not self.players_turn and not self.pause_for_analysis):
            sorted_words = self.generate_all_plays(self.computer.tiles)

            word_info = sorted_words[-3] # COMPUTER DIFFICULTY

            self.computer.tiles = self.play_word(word_info, self.computer.tiles)

            # this was copied
            tiles_needed         = 7 - len(self.computer.tiles)
            if tiles_needed == 7:
                self.letters_bingoed = self.letters_bingoed.union(self.letters_to_highlight)
            self.computer.tiles += TILE_BAG[self.tile_bag_index:self.tile_bag_index + tiles_needed]
            self.tile_bag_index += tiles_needed

            self.computer.last_word_score = word_info[0]
            self.computer.score          += word_info[0]
            self.players_turn             = True

            self.last_grid = copy.deepcopy(self.grid)

            print(self.player.score, self.computer.score)

        # PLAYER WORD SOLVER
        if (self.players_turn and not self.player_plays):
            self.player_plays = self.generate_all_plays(self.player.tiles)
            print("Done generating plays")

    def recursive_definition(self, word, num):
        definition = self.DEFINITIONS[word.upper()]
        if definition[0] not in ['<', '{']:
            return definition
        redirect_word = definition.split('=')[0][1:]
        # in case there is infinite recursion, break
        if num > 10:
            return definition
        return definition + ' || ' + self.recursive_definition(redirect_word, num + 1)

    def play_word(self, word_info, tiles):
        score, word, pos = word_info
        row, col, dir    = pos.tuple()

        row = 14 - row # lol, wtf was i thinking :s :s
        print(score, word, pos)

        row_delta = 1 if dir == Direction.DOWN else 0
        col_delta = 0 if dir == Direction.DOWN else 1

        prefix, _ = prefix_tiles(self.grid, dir, row, col)

        remaining_tiles = tiles
        for letter in word.removeprefix(prefix):
            if self.grid[row][col] == '.':
                self.letters_to_highlight.add((14-row, col))
                self.grid[row][col] = letter
                if remaining_tiles:
                    remaining_tiles.remove(letter)
            col += col_delta
            row += row_delta

        self.definition = self.recursive_definition(word, 1)
        return remaining_tiles

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

        if key in ARROW_KEYS:
            if not self.letters_typed:
                if self.pause_for_analysis:
                    if self.pause_for_analysis_rank == None:
                        self.pause_for_analysis_rank = 1
                    elif key == arcade.key.UP:
                        self.pause_for_analysis_rank = (self.pause_for_analysis_rank + 12) % 14 + 1
                    elif key == arcade.key.DOWN:
                        self.pause_for_analysis_rank = self.pause_for_analysis_rank % 14 + 1

                    self.grid = copy.deepcopy(self.last_grid)
                    self.letters_to_highlight.clear()
                    self.play_word(self.player_plays[-self.pause_for_analysis_rank], None)

                else:
                    if self.cursor == 0:
                        self.cursor = 1
                    else:
                        if modifiers == arcade.key.MOD_CTRL:
                            if key in [arcade.key.LEFT, arcade.key.RIGHT]:
                                self.cursor = 1
                            else:
                                self.cursor = 2
                            if key == arcade.key.LEFT:
                                while self.cursor_x >= 0 and self.grid[14 - self.cursor_y][self.cursor_x] == '.':
                                    self.cursor_x -= 1
                                self.cursor_x += 1
                            if key == arcade.key.RIGHT:
                                while self.cursor_x <= 14 and self.grid[14 - self.cursor_y][self.cursor_x] == '.':
                                    self.cursor_x += 1
                                self.cursor_x -= 1
                            if key == arcade.key.DOWN:
                                while self.cursor_y >= 0 and self.grid[14 - self.cursor_y][self.cursor_x] == '.':
                                    self.cursor_y -= 1
                                self.cursor_y += 1
                            if key == arcade.key.UP:
                                while self.cursor_y <= 14 and self.grid[14 - self.cursor_y][self.cursor_x] == '.':
                                    self.cursor_y += 1
                                self.cursor_y -= 1
                        else:
                            if key in [arcade.key.LEFT, arcade.key.RIGHT] and self.cursor == 2:
                                self.cursor = 1
                            elif key in [arcade.key.UP, arcade.key.DOWN] and self.cursor == 1:
                                self.cursor = 2
                            else:
                                if key == arcade.key.LEFT:  self.cursor_x = max( 0, self.cursor_x - 1)
                                if key == arcade.key.RIGHT: self.cursor_x = min(14, self.cursor_x + 1)
                                if key == arcade.key.UP:    self.cursor_y = min(14, self.cursor_y + 1)
                                if key == arcade.key.DOWN:  self.cursor_y = max( 0, self.cursor_y - 1)

        if str(chr(key)).isalpha():
            letter = chr(key - 32)
            letters_remaining = Counter(self.player.tiles) - Counter(self.letters_typed.values())
            if letter in letters_remaining:
                while self.cursor_y >= 0  and \
                      self.cursor_x <= 14 and \
                      self.grid[14-self.cursor_y][self.cursor_x] != '.':
                    if self.cursor == 1: self.cursor_x = min(15, self.cursor_x + 1)
                    if self.cursor == 2: self.cursor_y = max(-1, self.cursor_y - 1)

                if not (self.cursor_x > 14 or self.cursor_y < 0):
                    self.letters_typed[(self.cursor_y, self.cursor_x)] = letter
                    if self.cursor == 1: self.cursor_x = min(15, self.cursor_x + 1)
                    if self.cursor == 2: self.cursor_y = max(-1, self.cursor_y - 1)

                while self.cursor_y >= 0  and \
                      self.cursor_x <= 14 and \
                      self.grid[14-self.cursor_y][self.cursor_x] != '.':
                    if self.cursor == 1: self.cursor_x = min(15, self.cursor_x + 1)
                    if self.cursor == 2: self.cursor_y = max(-1, self.cursor_y - 1)

                word_info = self.is_playable_and_score_and_word()
                print(word_info)
                if word_info.is_ok():
                    try:
                        # TODO name that algorithm
                        rank = 1
                        while word_info.unwrap() != self.player_plays[-rank]:
                            rank += 1
                        self.player_words_found.add(rank)
                        self.player_scores_found.add(word_info.unwrap()[0])
                        self.definition = self.recursive_definition(word_info.unwrap()[1], 1)
                    except:
                        print("failure: score_word_lookup", word_info)
                        for wi in self.player_plays:
                            if wi[1] == word_info.unwrap()[1]:
                                print(wi)

        if key == arcade.key.ESCAPE:
            self.letters_typed.clear()
            self.hook_letters.clear()
            self.display_hook_letters = Hooks.OFF
            self.cursor_x = min(14, self.cursor_x)
            self.cursor_y = max(0, self.cursor_y)

        if key == arcade.key.BACKSPACE:
            if len(self.letters_typed):
                self.letters_typed.popitem()
                if self.cursor == 1: self.cursor_x -= 1
                if self.cursor == 2: self.cursor_y += 1
                while self.grid[14-self.cursor_y][self.cursor_x] != '.':
                    if self.cursor == 1: self.cursor_x -= 1
                    if self.cursor == 2: self.cursor_y += 1

        if key == arcade.key.SPACE:
            random.shuffle(self.player.tiles)

        if key == arcade.key.SLASH:
            if self.display_hook_letters in [Hooks.OFF, Hooks.ALL] :
                self.display_hook_letters = Hooks.ALL if self.display_hook_letters == Hooks.OFF else Hooks.ON_RACK
                self.hook_letters.clear()
                for row in range(0, 15):
                    for col in range(0,15):
                        # row-wise check
                        if col > 1:
                            if self.grid[row][col] != '.' and \
                                self.grid[row  ][col-1] == '.' and \
                                (row < 14 and self.grid[row+1][col-1] == '.') and \
                                (row > 0  and self.grid[row-1][col-1] == '.'):
                                suffix, _ = suffix_tiles(self.grid, Direction.ACROSS, row, col-1)
                                for w in self.DICTIONARY:
                                    if w[1:] == suffix and (self.display_hook_letters == Hooks.ALL or w[0] in self.player.tiles):
                                        self.hook_letters[(14-row, col-1)].append(w[0])
                        if col < 14:
                            if self.grid[row][col] != '.' and \
                                self.grid[row  ][col+1] == '.' and \
                                (row < 14 and self.grid[row+1][col+1] == '.') and \
                                (row > 0  and self.grid[row-1][col+1] == '.'):
                                prefix, _ = prefix_tiles(self.grid, Direction.ACROSS, row, col+1)
                                for w in self.DICTIONARY:
                                    if w[:-1] == prefix and (self.display_hook_letters == Hooks.ALL or w[-1] in self.player.tiles):
                                        self.hook_letters[(14-row, col+1)].append(w[-1])
                        # col-wise check
                        if row > 0:
                            if self.grid[row][col] != '.' and \
                                self.grid[row-1][col  ] == '.' and \
                                (col < 14 and self.grid[row-1][col+1] == '.') and \
                                (col > 0  and self.grid[row-1][col-1] == '.'):
                                suffix, _ = suffix_tiles(self.grid, Direction.DOWN, row-1, col)
                                for w in self.DICTIONARY:
                                    if w[1:] == suffix and (self.display_hook_letters == Hooks.ALL or w[0] in self.player.tiles):
                                        self.hook_letters[(14-(row-1), col)].append(w[0])
                        if row < 14:
                            if self.grid[row][col] != '.' and \
                                self.grid[row+1][col  ] == '.' and \
                                (col < 14 and self.grid[row+1][col+1] == '.') and \
                                (col > 0  and self.grid[row+1][col-1] == '.'):
                                prefix, _ = prefix_tiles(self.grid, Direction.DOWN, row+1, col)
                                for w in self.DICTIONARY:
                                    if w[:-1] == prefix and (self.display_hook_letters == Hooks.ALL or w[-1] in self.player.tiles):
                                        self.hook_letters[(14-(row+1), col)].append(w[-1])
            else:
                self.display_hook_letters = Hooks.OFF

        if key == arcade.key.ENTER:
            if self.pause_for_analysis:
                self.pause_for_analysis = False
                self.pause_for_analysis_rank = None
                self.player_plays = []
                self.player_scores_found.clear()
                self.player_words_found.clear()
                self.letters_to_highlight.clear()
                self.grid = copy.deepcopy(self.grid_backup)
                self.cursor_x = min(14, self.cursor_x)
                self.cursor_y = max(0, self.cursor_y)
            else:
                word_info = self.is_playable_and_score_and_word()
                if word_info.is_ok():
                    score, _, _ = word_info.unwrap()
                    self.player.score += score

                    for play in self.player_plays[-14:]:
                        print(play)

                    self.player.word_ranks.append(min(self.player_words_found))
                    print(('{:.1f}'.format(sum(self.player.word_ranks) / len(self.player.word_ranks))), self.player.word_ranks)

                    for (row, col), letter in self.letters_typed.items():
                        self.player.tiles.remove(letter)
                        self.grid[14-row][col] = letter
                    # we copy pasted the next three lines
                    tiles_needed                = 7 - len(self.player.tiles)
                    self.player.tiles          += TILE_BAG[self.tile_bag_index:self.tile_bag_index + tiles_needed]
                    self.player.last_word_score = score
                    self.tile_bag_index        += tiles_needed
                    self.players_turn           = False
                    self.pause_for_analysis     = True
                    self.grid_backup            = copy.deepcopy(self.grid)
                    self.cursor                 = 0
                    if tiles_needed == 7:
                        self.letters_bingoed = self.letters_bingoed.union(self.letters_typed.keys())
                    self.letters_typed.clear()

    def is_playable(self):
        return self.is_playable_and_score_and_word().is_ok()

    def is_playable_and_score_and_word(self):
        if len(self.letters_typed):
            start_row, start_col = next(iter(self.letters_typed))
            dir     = Direction.ACROSS if self.cursor == 1 else Direction.DOWN
            pos     = Position(dir, start_row, start_col) # start row is super hacky
            letters = ''.join(self.letters_typed.values())
            return word_score(self.grid, self.DICTIONARY, letters, pos, True, self.PREFIXES)
        return Err('no letters typed')

    def generate_all_plays(self, tiles):
        words = {''.join(p) for i in range(7, 0, -1) for p in it.permutations(tiles, i)}
        scores = Parallel(n_jobs=15, verbose=20)\
            (delayed(word_scores_for_row)\
                (self.grid, self.DICTIONARY, row, words, self.PREFIXES) for row in range(15))
        return sorted(mt.flatten(scores))

def main():

    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()

if __name__ == "__main__":
    main()
