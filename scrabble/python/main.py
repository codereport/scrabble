"""
HookStar Scrabble Trainer

Started from https://arcade.academy/examples/array_backed_grid.html#array-backed-grid
"""

# -*- coding: utf-8 -*-

import os
import random
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from enum import Enum

import arcade
from colorama import Fore, Style, init
from optional import Optional
from result import Err, Ok
import textwrap

from board import Board, Direction, Position
from solver import SolverState
from trie import nwl_2020

# Initialize colorama
init(autoreset=True)

## Constants

ROW_COUNT    = 15
COLUMN_COUNT = 15
WIDTH        = 50  # Grid width
HEIGHT       = 50  # Grid height
MARGIN       = 5   # This sets the margin between each cell and on the edges of the screen.

BOTTOM_MARGIN = 100
RIGHT_MARGIN  = 800

#FONT = "mono" if os.name == "posix" else "consolas"
FONT = "jetbrains mono"

SCREEN_WIDTH  = (WIDTH + MARGIN)  * COLUMN_COUNT + MARGIN + RIGHT_MARGIN
SCREEN_HEIGHT = (HEIGHT + MARGIN) * ROW_COUNT    + MARGIN + BOTTOM_MARGIN
SCREEN_TITLE  = "HookStar 🏴‍☠️⭐"

FONT_SIZE         = 30
HORIZ_TEXT_OFFSET = 13
VERT_TEXT_OFFSET  = 15

class Tl(Enum):
    NO = 1
    DL = 2
    DW = 3
    TL = 4
    TW = 5

BOARD = [[Tl.TW, Tl.NO, Tl.NO, Tl.DL, Tl.NO, Tl.NO, Tl.NO, Tl.TW, Tl.NO, Tl.NO, Tl.NO, Tl.DL, Tl.NO, Tl.NO, Tl.TW],
         [Tl.NO, Tl.DW, Tl.NO, Tl.NO, Tl.NO, Tl.TL, Tl.NO, Tl.NO, Tl.NO, Tl.TL, Tl.NO, Tl.NO, Tl.NO, Tl.DW, Tl.NO],
         [Tl.NO, Tl.NO, Tl.DW, Tl.NO, Tl.NO, Tl.NO, Tl.DL, Tl.NO, Tl.DL, Tl.NO, Tl.NO, Tl.NO, Tl.DW, Tl.NO, Tl.NO],
         [Tl.DL, Tl.NO, Tl.NO, Tl.DW, Tl.NO, Tl.NO, Tl.NO, Tl.DL, Tl.NO, Tl.NO, Tl.NO, Tl.DW, Tl.NO, Tl.NO, Tl.DL],
         [Tl.NO, Tl.NO, Tl.NO, Tl.NO, Tl.DW, Tl.NO, Tl.NO, Tl.NO, Tl.NO, Tl.NO, Tl.DW, Tl.NO, Tl.NO, Tl.NO, Tl.NO],
         [Tl.NO, Tl.TL, Tl.NO, Tl.NO, Tl.NO, Tl.TL, Tl.NO, Tl.NO, Tl.NO, Tl.TL, Tl.NO, Tl.NO, Tl.NO, Tl.TL, Tl.NO],
         [Tl.NO, Tl.NO, Tl.DL, Tl.NO, Tl.NO, Tl.NO, Tl.DL, Tl.NO, Tl.DL, Tl.NO, Tl.NO, Tl.NO, Tl.DL, Tl.NO, Tl.NO],
         [Tl.TW, Tl.NO, Tl.NO, Tl.DL, Tl.NO, Tl.NO, Tl.NO, Tl.DW, Tl.NO, Tl.NO, Tl.NO, Tl.DL, Tl.NO, Tl.NO, Tl.TW],
         [Tl.NO, Tl.NO, Tl.DL, Tl.NO, Tl.NO, Tl.NO, Tl.DL, Tl.NO, Tl.DL, Tl.NO, Tl.NO, Tl.NO, Tl.DL, Tl.NO, Tl.NO],
         [Tl.NO, Tl.TL, Tl.NO, Tl.NO, Tl.NO, Tl.TL, Tl.NO, Tl.NO, Tl.NO, Tl.TL, Tl.NO, Tl.NO, Tl.NO, Tl.TL, Tl.NO],
         [Tl.NO, Tl.NO, Tl.NO, Tl.NO, Tl.DW, Tl.NO, Tl.NO, Tl.NO, Tl.NO, Tl.NO, Tl.DW, Tl.NO, Tl.NO, Tl.NO, Tl.NO],
         [Tl.DL, Tl.NO, Tl.NO, Tl.DW, Tl.NO, Tl.NO, Tl.NO, Tl.DL, Tl.NO, Tl.NO, Tl.NO, Tl.DW, Tl.NO, Tl.NO, Tl.DL],
         [Tl.NO, Tl.NO, Tl.DW, Tl.NO, Tl.NO, Tl.NO, Tl.DL, Tl.NO, Tl.DL, Tl.NO, Tl.NO, Tl.NO, Tl.DW, Tl.NO, Tl.NO],
         [Tl.NO, Tl.DW, Tl.NO, Tl.NO, Tl.NO, Tl.TL, Tl.NO, Tl.NO, Tl.NO, Tl.TL, Tl.NO, Tl.NO, Tl.NO, Tl.DW, Tl.NO],
         [Tl.TW, Tl.NO, Tl.NO, Tl.DL, Tl.NO, Tl.NO, Tl.NO, Tl.TW, Tl.NO, Tl.NO, Tl.NO, Tl.DL, Tl.NO, Tl.NO, Tl.TW]]

TILE_SCORE = {
    "A": 1, "B": 3, "C": 3, "D": 2, "E": 1, "F": 4,  "G": 2,  "H": 4, "I": 1, "J": 8,
    "K": 5, "L": 1, "M": 3, "N": 1, "O": 1, "P": 3,  "Q": 10, "R": 1, "S": 1, "T": 1,
    "U": 1, "V": 4, "W": 4, "X": 8, "Y": 4, "Z": 10, " ": 0 }

TILE_BAG = \
    ["A"] * 9 + ["B"] * 2 + ["C"] * 2 + ["D"] * 4 + ["E"] * 12 + ["F"] * 2 + ["G"] * 3 + \
    ["H"] * 2 + ["I"] * 9 + ["J"] * 1 + ["K"] * 1 + ["L"] * 4  + ["M"] * 2 + ["N"] * 6 + \
    ["O"] * 8 + ["P"] * 2 + ["Q"] * 1 + ["R"] * 6 + ["S"] * 4  + ["T"] * 6 + ["U"] * 4 + \
    ["V"] * 2 + ["W"] * 2 + ["X"] * 1 + ["Y"] * 2 + ["Z"] * 1  + [" "] * 2

LR_ARROW_KEYS = [arcade.key.LEFT, arcade.key.RIGHT]
UD_ARROW_KEYS = [arcade.key.UP, arcade.key.DOWN]
ARROW_KEYS    = LR_ARROW_KEYS + UD_ARROW_KEYS

COLOR_NORMAL        = (200, 196, 172)
COLOR_TRIPLE_WORD   = (241, 108,  77)
COLOR_TRIPLE_LETTER = ( 58, 156, 184)
COLOR_DOUBLE_WORD   = (250, 187, 170)
COLOR_DOUBLE_LETTER = (189, 215, 214)

## Enumerators & Helper Classes

class LogType(Enum):
    FAIL = 0,
    INFO = 1,
    OK = 2

DEBUG = True

def log(msg: str, type: LogType):
    if DEBUG:
        if type == LogType.FAIL: color = Fore.RED
        if type == LogType.INFO: color = Fore.YELLOW
        if type == LogType.OK:   color = Fore.GREEN
        print(color + "DEBUG: "+ Style.RESET_ALL + msg)

class Hooks(Enum):
    OFF     = 0
    ALL     = 1
    ON_RACK = 2

class Extension(Enum):
    PREFIX = 1
    SUFFIX = 2

class Phase(Enum):
    PLAYERS_TURN       = 1
    PAUSE_FOR_ANALYSIS = 2
    COMPUTERS_TURN     = 3

@dataclass(frozen=True, order=True)
class Play:
    score:    int
    word:     str
    pos:      Position
    is_bingo: bool
    blanks:   set()

class Cursor:
    def __init__(self):
        self.dir = Optional.empty()
        self.x   = 7
        self.y   = 7

    def rotate_dir(self):
        if   self.dir.is_empty():                self.dir = Optional.of(Direction.ACROSS)
        elif self.dir.get() == Direction.ACROSS: self.dir = Optional.of(Direction.DOWN)
        else:                                    self.dir = Optional.empty()

class Player:
    def __init__(self, tiles):
        self.tiles           = tiles
        self.score           = 0
        self.word_ranks      = []
        self.last_word_score = 0

## Free functions

def word_wrap_split(text: str, line_length: int):
    wrapper = textwrap.TextWrapper(width=line_length)
    lines = wrapper.wrap(text)
    return lines

def letter_multiplier(row, col):
    if BOARD[row][col] == Tl.DL: return 2
    if BOARD[row][col] == Tl.TL: return 3
    return 1

def word_multiplier(row, col):
    if BOARD[row][col] == Tl.DW: return 2
    if BOARD[row][col] == Tl.TW: return 3
    return 1

def tile_color(pos):
    row, col = pos
    if BOARD[row][col] == Tl.DL: return COLOR_DOUBLE_LETTER
    if BOARD[row][col] == Tl.DW: return COLOR_DOUBLE_WORD
    if BOARD[row][col] == Tl.TL: return COLOR_TRIPLE_LETTER
    if BOARD[row][col] == Tl.TW: return COLOR_TRIPLE_WORD
    return COLOR_NORMAL

def deltas(dir):
    row_delta = 1 if dir == Direction.DOWN else 0
    col_delta = 0 if dir == Direction.DOWN else 1
    return (row_delta, col_delta)

def extension_tiles(ext, board, dir, row, col, blank_poss):
    delta_factor         = -1 if ext == Extension.PREFIX else 1
    row_delta, col_delta = tuple(delta_factor * i for i in list(deltas(dir)))
    next_row, next_col, tiles, score = row, col, "", 0
    while True:
        next_row += row_delta
        next_col += col_delta
        pos = (next_row, next_col)
        if board.is_filled(pos):
            tiles += board.tile(pos)
            if (14 - next_row, next_col) not in blank_poss:
                score += TILE_SCORE.get(board.tile(pos))
        else:
            break
    return (tiles[::delta_factor], score)

def prefix_tiles(board, dir, row, col, blank_poss):
    return extension_tiles(Extension.PREFIX, board, dir, row, col, blank_poss)

def suffix_tiles(board, dir, row, col, blank_poss):
    return extension_tiles(Extension.SUFFIX, board, dir, row, col, blank_poss)

def word_score(board, dictionary, letters, pos, first_call, blank_poss):
    dir, row, col = pos.dir, 14 - pos.row, pos.col
    if board.is_filled((row, col)):
        return Err("cannot start word on existing tile")
    rest_of_row = board._tiles[row][col:] if dir == Direction.ACROSS else list(zip(*board._tiles))[col][row:]
    if len([1 for c in rest_of_row if c == "."]) < len(letters):
        return Err("outside of board")

    word_played, score   = prefix_tiles(board, dir, row, col, blank_poss)
    has_prefix           = len(word_played) > 0
    word_mult            = 1
    row_delta, col_delta = deltas(dir)
    crosses              = len(word_played) > 0
    valid_start          = False
    blanks               = set()
    letters_played       = 0

    perpandicular_words = []

    for letter in letters:
        while board.is_filled((row, col)):
            word_played = word_played + board.tile((row, col))
            if (14 - row, col) not in blank_poss:
                score  += TILE_SCORE.get(board.tile((row, col)))
            row        += row_delta
            col        += col_delta
            crosses     = True
        letters_played += 1
        word_played    += letter
        word_mult      *= word_multiplier(row, col)
        if (14 - row, col) not in blank_poss:
            score += TILE_SCORE.get(letter) * letter_multiplier(row, col)
        else:
            blanks.add((14 - row, col))
        if len(letters) == 1:
            one_letter_score = TILE_SCORE.get(letter) * letter_multiplier(row, col)

        # find perpendicular words that need to be scored
        if dir == Direction.ACROSS:
            if board.is_filled((row + 1, col)) or board.is_filled((row - 1, col)):
                perpandicular_words.append((letter, (row, col)))
        else:
            if board.is_filled((row, col + 1)) or board.is_filled((row, col - 1)):
                perpandicular_words.append((letter, (row, col)))
        if row * col == 49:
            valid_start = True
        row += row_delta
        col += col_delta

    suffix, suffix_score = suffix_tiles(board, dir, row - row_delta, col - col_delta, blank_poss)
    word_played         += suffix
    has_suffix           = len(suffix) > 0

    score += suffix_score

    if not has_prefix and not has_suffix and len(letters) == 1:
        score -= one_letter_score

    score *= word_mult
    score += 50 if len(letters) == 7 else 0

    if not crosses and len(suffix) == 0 and len(perpandicular_words) == 0 and first_call:
        if board.is_first_turn():
            if not valid_start:
                return Err("first move must be through center tile")
        else:
            return Err("does not overlap with any other word")

    if first_call:
        opposite_dir = Direction.ACROSS if dir == Direction.DOWN else Direction.DOWN
        for word, (r, c) in perpandicular_words:
            new_pos = Position(opposite_dir, 14-r, c)
            potential_play = word_score(board, dictionary, word, new_pos, False, blank_poss)
            if potential_play.is_ok():
                play = potential_play.unwrap()
                score += play.score
                if len(word_played) == 1:
                    word_played = play.word
            else:
                return potential_play

    if not dictionary.is_word(word_played) and not (len(word_played) == 1 and len(perpandicular_words)):
        return Err(f"{word_played} not in dictionary")

    return Ok(Play(score, word_played, pos, letters_played == 7, blanks))

class MyGame(arcade.Window):
    """Main application class"""

    def __init__(self, width, height, title):
        """Set up the application"""

        super().__init__(width, height, title)

        # Create a 2 dimensional array. A two dimensional array is simply a list of lists.
        self.grid        = Board()
        self.grid_backup = self.grid.copy()
        self.last_grid   = self.grid.copy()

        arcade.set_background_color(arcade.color.BLACK)

        self.cursor = Cursor()

        # Setup game
        random.shuffle(TILE_BAG)
        self.tile_bag_index = 14

        self.player   = Player(TILE_BAG[0: 7])
        self.computer = Player(TILE_BAG[7:14])

        self.phase                   = Phase.PLAYERS_TURN
        self.pause_for_analysis_rank = None
        self.player_plays            = []
        self.player_words_found      = set() # by rank
        self.player_scores_found     = set()

        self.hook_letters         = defaultdict(set)
        self.display_hook_letters = Hooks.OFF

        self.DEFINITIONS = dict()
        with open("../dictionary/nwl_2020.txt") as f:
            for line in f:
                words = line.strip().split()
                self.DEFINITIONS[words[0]] = " ".join(words[1:])

        # this is a set of words that the computer can't play
        # it forces the computer to use words you don't know so
        # you can expand your vocabulary
        self.KNOW = set()
        with open("know.txt") as f:
            for line in f:
                word = line.strip()
                self.KNOW.add(word)

        self.trie = nwl_2020()

        self.letters_typed        = {}
        self.letters_to_highlight = set()
        self.letters_bingoed      = set()
        self.temp_blank_letters   = set()
        self.blank_letters        = set()
        self.just_bingoed         = False
        self.definition           = ""
        self.game_over            = False

    def draw_letter(self, letter, x, y, color, pos):
        arcade.draw_rectangle_filled(x, y, WIDTH, HEIGHT, color)
        if not self.just_bingoed and pos in self.letters_bingoed:
            arcade.draw_rectangle_outline(x, y, WIDTH-4, HEIGHT-4, arcade.color.DARK_PASTEL_GREEN, 5)
        arcade.draw_text(letter, x-HORIZ_TEXT_OFFSET, y-VERT_TEXT_OFFSET, arcade.color.WHITE, FONT_SIZE, bold=True, font_name=FONT)
        # if letter.isupper():

    def on_draw(self):
        """Render the screen"""

        arcade.start_render()

        played_tile_color = arcade.color.DARK_PASTEL_GREEN if self.is_playable() else arcade.color.SAE

        # Draw the grid
        for row in range(ROW_COUNT):
            board_row = 14 - row
            for column in range(COLUMN_COUNT):
                bpos = (board_row, column)
                pos = (row, column)
                color = tile_color(pos) if self.grid.is_empty(bpos) else arcade.color.AMETHYST
                if pos in self.letters_typed:
                    color = played_tile_color
                elif pos in self.letters_to_highlight:
                    color = arcade.color.HOT_PINK

                x = (MARGIN + WIDTH)  * column + MARGIN + WIDTH  // 2
                y = (MARGIN + HEIGHT) * row    + MARGIN + HEIGHT // 2 + BOTTOM_MARGIN

                if   self.grid.is_filled(bpos): letter = self.grid.tile(bpos)
                elif pos in self.letters_typed: letter = self.letters_typed.get(pos)
                else:                           letter = " "

                blank = pos in self.temp_blank_letters | self.blank_letters
                if blank:
                    letter = letter.lower()
                self.draw_letter(letter, x, y, color, pos)

                if pos not in self.letters_typed and self.display_hook_letters != Hooks.OFF and pos in self.hook_letters:
                    text_color = arcade.color.WHITE if color in [COLOR_TRIPLE_LETTER, COLOR_TRIPLE_WORD] else arcade.color.BLACK
                    letters = self.hook_letters[pos]
                    xd, yd = 0, 0
                    for letter in letters:
                        arcade.draw_text(letter, x - WIDTH / 2.35 + xd, y + HEIGHT / 3.4 - yd, text_color, 10, bold=True, font_name=FONT)
                        xd += 12
                        if xd == 48:
                            xd  = 0
                            yd += 11

        # Draw cursor
        if self.cursor.dir.is_present() and len(self.letters_typed) == 0:
            arrow = "→" if self.cursor.dir.get() == Direction.ACROSS else "↓"
            x = (MARGIN + WIDTH)  * self.cursor.x + MARGIN + WIDTH  // 2
            y = (MARGIN + HEIGHT) * self.cursor.y + MARGIN + HEIGHT // 2 + BOTTOM_MARGIN
            self.draw_letter(arrow, x, y, arcade.color.BLACK, None)

        # Draw blue score boxes (for player)
        column = 15
        row    = 14
        color  = COLOR_DOUBLE_LETTER
        x = (MARGIN + WIDTH)  * column + MARGIN * 2 + (WIDTH * 3.5)  // 2
        y = (MARGIN + HEIGHT) * row    + MARGIN + HEIGHT // 2 + BOTTOM_MARGIN
        arcade.draw_rectangle_filled(x, y, WIDTH * 3.5, HEIGHT, color)
        score = f"{self.player.score} ({self.player.last_word_score})"
        arcade.draw_text(score, x-HORIZ_TEXT_OFFSET*4, y-VERT_TEXT_OFFSET*.75, arcade.color.BLACK, 20, bold=True, font_name=FONT)

        # Draw pink score box (for computer)
        column = 15
        row    = 14
        color  = COLOR_DOUBLE_WORD
        x = (MARGIN + WIDTH)  * column + (MARGIN + (WIDTH * 3.5)) + MARGIN * 2 + (WIDTH * 3.5)  // 2
        y = (MARGIN + HEIGHT) * row    + MARGIN + HEIGHT // 2 + BOTTOM_MARGIN
        arcade.draw_rectangle_filled(x, y, WIDTH * 3.5, HEIGHT, color)
        score = f"{self.computer.score} ({self.computer.last_word_score})"
        arcade.draw_text(score, x-HORIZ_TEXT_OFFSET*4, y-VERT_TEXT_OFFSET*.75, arcade.color.BLACK, 20, bold=True, font_name=FONT)

        # Draw top word boxes
        for row in range(ROW_COUNT - 1):
            render_row = 14 - row # and place
            if len(self.player_plays) == 0 or render_row + 1 > len(self.player_plays):
                continue
            column = 15
            play = self.player_plays[-render_row]
            if self.phase == Phase.PAUSE_FOR_ANALYSIS and self.pause_for_analysis_rank == render_row:
                color = arcade.color.HOT_PINK
            elif render_row in self.player_words_found:
                color = arcade.color.DARK_PASTEL_GREEN
            elif play.score in self.player_scores_found:
                color = arcade.color.YELLOW
            else:
                color = arcade.color.LIGHT_GRAY
            TOP_WORD_BOX_WIDTH = (MARGIN // 2 + (WIDTH * 3.5)) * 2 # noqa: N806
            x = (MARGIN + WIDTH)  * column + (2 * MARGIN) + TOP_WORD_BOX_WIDTH // 2
            y = (MARGIN + HEIGHT) * row    + MARGIN + HEIGHT // 2 + BOTTOM_MARGIN
            arcade.draw_rectangle_filled(x, y, TOP_WORD_BOX_WIDTH, HEIGHT, color)
            if render_row in self.player_words_found or self.phase == Phase.PAUSE_FOR_ANALYSIS:
                arcade.draw_rectangle_filled(x, y, TOP_WORD_BOX_WIDTH, HEIGHT, color)
                display = f"{render_row}: {play.word} ({play.score})"
                arcade.draw_text(display, x-HORIZ_TEXT_OFFSET-130, y-VERT_TEXT_OFFSET*.75, arcade.color.BLACK, 20, bold=True, font_name=FONT)

        # Draw tile rack
        tiles_left = list(self.letters_typed.values())
        blanks_typed = len(self.temp_blank_letters)
        for i, tile in enumerate(self.player.tiles):
            if self.phase == Phase.PLAYERS_TURN and tile in tiles_left:
                color = played_tile_color
                tiles_left.remove(tile)
            elif self.phase == Phase.PLAYERS_TURN and blanks_typed > 0 and tile == " ":
                color = played_tile_color
                blanks_typed -= 1
            else:
                color = arcade.color.AMETHYST
            x = (4 + i) * (MARGIN + WIDTH) + MARGIN + WIDTH // 2
            y = 50

            self.draw_letter(tile, x, y, color, None)

        # Draw word definition
        x = 12 * (MARGIN + WIDTH) + MARGIN + WIDTH // 2
        y = 50
        emoji = ""
        if "fish"     in self.definition: emoji = "🐟 "
        if "tree"     in self.definition: emoji = "🌲 "
        if "insect"   in self.definition: emoji = "🐛 "
        if "plant"    in self.definition: emoji = "🌱 "
        if "monetary" in self.definition: emoji = "💲 "
        if "bird"     in self.definition: emoji = "🐦 "

        lines = word_wrap_split(f"{emoji}{self.definition}", 80)
        for i, line in enumerate(lines):
            arcade.draw_text(line, x-HORIZ_TEXT_OFFSET, y-VERT_TEXT_OFFSET + (25 * (1 - i)), arcade.color.WHITE, 15, font_name=FONT, bold=True)

        left     = max(0, 100 - self.tile_bag_index + len(self.computer.tiles))
        tile_bag = " ".join(f"{a}:{b}" for a,b in sorted(Counter(TILE_BAG[self.tile_bag_index:] + self.computer.tiles).items()))
        x = 21 * (MARGIN + WIDTH) + MARGIN + WIDTH // 2
        y = 500
        arcade.draw_text(f"{left} {tile_bag}", x-HORIZ_TEXT_OFFSET, y-VERT_TEXT_OFFSET, arcade.color.WHITE, 15, font_name=FONT, bold=True)

        if self.game_over:
            os.remove("know.txt")
            f = open("know.txt", "x")
            f.write("\n".join(sorted(list(self.KNOW))))
            f.close()
            _ = input("Press ENTER to exit.")
            sys.exit()
            return

        if len(self.player.tiles) == 0 or len(self.computer.tiles) == 0:
            self.game_over = True
            if len(self.computer.tiles):
                extra_points = 2 * sum(TILE_SCORE.get(c) for c in self.computer.tiles)
                self.player.score += extra_points
            else:
                extra_points = 2 * sum(TILE_SCORE.get(c) for c in self.player.tiles)
                self.computer.score += extra_points
            print(f"{extra_points=}")
            print("GAME OVER")

        # COMPUTER LOGIC
        if self.phase == Phase.COMPUTERS_TURN:
            sorted_words = self.generate_all_plays(self.computer.tiles)

            i = -1
            while sorted_words[i].word in self.KNOW:
                i -= 1
                log(f"skip {sorted_words[i].word} ({i})", LogType.INFO)
            play  = sorted_words[i]

            # add computers played word to dictionary if you know it
            if play.word not in self.KNOW:
                know = input(f"Do you know: {play.word}? ")
                if know.lower() == "y":
                    self.KNOW.add(play.word)

            self.blank_letters = self.blank_letters | play.blanks

            self.computer.tiles = self.play_word(play, self.computer.tiles)

            # this was copied
            tiles_needed = 7 - len(self.computer.tiles)
            if play.is_bingo:
                self.letters_bingoed = self.letters_bingoed.union(self.letters_to_highlight)
            self.computer.tiles += TILE_BAG[self.tile_bag_index:self.tile_bag_index + tiles_needed]
            self.tile_bag_index += tiles_needed

            self.computer.last_word_score = play.score
            self.computer.score          += play.score
            self.phase                    = Phase.PLAYERS_TURN

            self.last_grid = self.grid.copy()

        # PLAYER WORD SOLVER
        if (self.phase == Phase.PLAYERS_TURN and not self.player_plays):
            self.player_plays = self.generate_all_plays(self.player.tiles)
            log("Done generating plays", LogType.OK)

    def recursive_definition(self, word, num):
        definition = self.DEFINITIONS[word.upper()]
        if definition[0] not in ["<", "{"]:
            return definition
        redirect_word = definition.split("=")[0][1:]
        # in case there is infinite recursion, break
        if num > 10:
            return definition
        return f"{definition} || {self.recursive_definition(redirect_word, num + 1)}"

    def play_word(self, play, tiles):
        # TODO fix the 14 - row
        row, col             = 14 - play.pos.row, play.pos.col
        row_delta, col_delta = deltas(play.pos.dir)
        prefix, _            = prefix_tiles(self.grid, play.pos.dir, row, col, self.blank_letters)
        remaining_tiles      = tiles
        word                 = play.word
        for letter in word.removeprefix(prefix):
            if self.grid.is_empty((row, col)):
                self.letters_to_highlight.add((14 - row, col))
                self.grid.set_tile((row, col), letter)
                if remaining_tiles:
                    if letter in remaining_tiles:
                        remaining_tiles.remove(letter)
                    elif " " in remaining_tiles:
                        remaining_tiles.remove(" ")
            col += col_delta
            row += row_delta

        self.definition = self.recursive_definition(word, 1)
        return remaining_tiles

    def on_mouse_press(self, x, y, button, modifiers):
        """Called when the user presses a mouse button"""

        if self.letters_typed:
            return

        # Change the x/y screen coordinates to grid coordinates
        column = int(x // (WIDTH + MARGIN))
        row    = int((y - BOTTOM_MARGIN) // (HEIGHT + MARGIN))

        self.cursor.x = column
        self.cursor.y = row
        self.cursor.rotate_dir()

        log(f"Click coordinates: ({x}, {y}). Grid coordinates: ({row}, {column})", LogType.OK)

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key"""

        if key in ARROW_KEYS:
            if not self.letters_typed:
                if self.phase == Phase.PAUSE_FOR_ANALYSIS:
                    if self.pause_for_analysis_rank is None:
                        self.pause_for_analysis_rank = 1
                    elif key == arcade.key.UP:
                        self.pause_for_analysis_rank = (self.pause_for_analysis_rank + 12) % 14 + 1
                    elif key == arcade.key.DOWN:
                        self.pause_for_analysis_rank = self.pause_for_analysis_rank % 14 + 1

                    self.grid = self.last_grid.copy()
                    self.letters_to_highlight.clear()
                    self.play_word(self.player_plays[-self.pause_for_analysis_rank], None)

                else:
                    if self.cursor.dir.is_empty():
                        self.cursor.dir = Optional.of(Direction.ACROSS)
                    else:
                        if modifiers == arcade.key.MOD_CTRL:
                            self.cursor.dir = Optional.of(Direction.ACROSS if key in LR_ARROW_KEYS else Direction.DOWN)
                            xd = -1 if key == arcade.key.LEFT else 1 if key == arcade.key.RIGHT else 0
                            yd = -1 if key == arcade.key.DOWN else 1 if key == arcade.key.UP    else 0
                            while self.grid.is_empty((14 - (self.cursor.y + yd), self.cursor.x + xd)):
                                self.cursor.x += xd
                                self.cursor.y += yd
                        else:
                            if key in LR_ARROW_KEYS and self.cursor.dir.get() == Direction.DOWN:
                                self.cursor.dir = Optional.of(Direction.ACROSS)
                            elif key in UD_ARROW_KEYS and self.cursor.dir.get() == Direction.ACROSS:
                                self.cursor.dir = Optional.of(Direction.DOWN)
                            else:
                                if key == arcade.key.LEFT:  self.cursor.x = max( 0, self.cursor.x - 1)
                                if key == arcade.key.RIGHT: self.cursor.x = min(14, self.cursor.x + 1)
                                if key == arcade.key.UP:    self.cursor.y = min(14, self.cursor.y + 1)
                                if key == arcade.key.DOWN:  self.cursor.y = max( 0, self.cursor.y - 1)

        elif str(chr(key)).isalpha():
            letter = chr(key - 32)
            letters_remaining = self.player.tiles.copy()
            for c in self.letters_typed.values():
                to_remove = c if c in letters_remaining else " "
                letters_remaining.remove(to_remove)
            need_blank = False
            if letter not in letters_remaining and " " in letters_remaining:
                need_blank = True
                letters_remaining.remove(" ")
                letters_remaining.append(letter)

            if letter in letters_remaining:
                while self.grid.is_filled((14-self.cursor.y, self.cursor.x)):
                    if self.cursor.dir.get() == Direction.ACROSS: self.cursor.x = min(15, self.cursor.x + 1)
                    if self.cursor.dir.get() == Direction.DOWN:   self.cursor.y = max(-1, self.cursor.y - 1)

                if not (self.cursor.x > 14 or self.cursor.y < 0):
                    self.letters_typed[(self.cursor.y, self.cursor.x)] = letter
                    if need_blank:
                        self.temp_blank_letters.add((self.cursor.y, self.cursor.x))
                    if self.cursor.dir.get() == Direction.ACROSS: self.cursor.x = min(15, self.cursor.x + 1)
                    if self.cursor.dir.get() == Direction.DOWN:   self.cursor.y = max(-1, self.cursor.y - 1)

                while self.grid.is_filled((14-self.cursor.y, self.cursor.x)):
                    if self.cursor.dir.get() == Direction.ACROSS: self.cursor.x = min(15, self.cursor.x + 1)
                    if self.cursor.dir.get() == Direction.DOWN:   self.cursor.y = max(-1, self.cursor.y - 1)

                potential_play = self.is_playable_and_score_and_word()
                print(potential_play)
                if potential_play.is_ok():
                    play = potential_play.unwrap()
                    try:
                        rank = self.player_plays[::-1].index(play) + 1
                        self.player_words_found.add(rank)
                        self.player_scores_found.add(play.score)
                        self.definition = self.recursive_definition(play.word, 1)
                    except Exception:
                        log(f"failed to play: {play}", LogType.FAIL)

        if key == arcade.key.ESCAPE:
            self.letters_typed.clear()
            self.temp_blank_letters.clear()
            self.cursor.x = min(14, self.cursor.x)
            self.cursor.y = max(0, self.cursor.y)

        if key == arcade.key.BACKSPACE:
            if len(self.letters_typed):
                self.letters_typed.popitem()
                if self.cursor.dir.get() == Direction.ACROSS: self.cursor.x -= 1
                if self.cursor.dir.get() == Direction.DOWN:   self.cursor.y += 1
                while self.grid.is_filled((14-self.cursor.y, self.cursor.x)):
                    if self.cursor.dir.get() == Direction.ACROSS: self.cursor.x -= 1
                    if self.cursor.dir.get() == Direction.DOWN:   self.cursor.y += 1
                pos = (self.cursor.y, self.cursor.x)
                if pos in self.temp_blank_letters:
                    self.temp_blank_letters.remove(pos)

        if key == arcade.key.SPACE:
            random.shuffle(self.player.tiles)

        if key == arcade.key.SLASH:
            if self.display_hook_letters in [Hooks.OFF, Hooks.ALL] :
                self.display_hook_letters = Hooks.ALL if self.display_hook_letters == Hooks.OFF else Hooks.ON_RACK
                self.hook_letters.clear()
                solver = SolverState(self.trie, self.grid, self.player.tiles)
                hooks = solver.cross_check_for_display(self.display_hook_letters == Hooks.ON_RACK)
                for pos in self.grid.all_positions():
                    row, col = pos
                    self.hook_letters[(14 - row, col)] = hooks[pos]
            else:
                self.display_hook_letters = Hooks.OFF

        if key == arcade.key.ENTER:
            if self.phase == Phase.PAUSE_FOR_ANALYSIS:
                self.phase                   = Phase.COMPUTERS_TURN
                self.pause_for_analysis_rank = None
                self.player_plays            = []
                self.just_bingoed            = False
                self.display_hook_letters    = Hooks.OFF
                self.hook_letters.clear()
                self.player_scores_found.clear()
                self.player_words_found.clear()
                self.letters_to_highlight.clear()
                self.grid = self.grid_backup.copy()
                self.cursor.x = min(14, self.cursor.x)
                self.cursor.y = max(0, self.cursor.y)
                self.blank_letters = self.blank_letters | self.temp_blank_letters
                self.temp_blank_letters.clear()

            else:
                assert self.phase == Phase.PLAYERS_TURN
                potential_play = self.is_playable_and_score_and_word()
                if potential_play.is_ok():
                    log("word is ok", LogType.OK)
                    play                        = potential_play.unwrap()
                    self.player.score          += play.score
                    self.player.last_word_score = play.score

                    if self.player_words_found:
                        # TODO: is this if statement needed
                        self.player.word_ranks.append(min(self.player_words_found))
                        print(("{:.1f}".format(sum(self.player.word_ranks) / len(self.player.word_ranks))), self.player.word_ranks)
                    else:
                        breakpoint()

                    for (row, col), letter in self.letters_typed.items():
                        if (row, col) in self.temp_blank_letters:
                            self.player.tiles.remove(" ")
                        else:
                            self.player.tiles.remove(letter)
                        self.grid.set_tile((14-row, col), letter)
                    # we copy pasted the next three lines
                    tiles_needed                = 7 - len(self.player.tiles)
                    self.player.tiles          += TILE_BAG[self.tile_bag_index:self.tile_bag_index + tiles_needed]
                    self.tile_bag_index        += tiles_needed
                    self.phase                  = Phase.PAUSE_FOR_ANALYSIS
                    self.grid_backup            = self.grid.copy()
                    self.cursor.dir             = Optional.empty()
                    if play.is_bingo:
                        self.letters_bingoed = self.letters_bingoed.union(self.letters_typed.keys())
                        self.just_bingoed    = True
                    self.letters_typed.clear()
                    self.hook_letters.clear()

    def is_playable(self):
        return self.is_playable_and_score_and_word().is_ok()

    def is_playable_and_score_and_word(self):
        if len(self.letters_typed):
            start_row, start_col = next(iter(self.letters_typed))
            dir     = self.cursor.dir.get()
            pos     = Position(dir, start_row, start_col) # start row is super hacky
            letters = "".join(self.letters_typed.values())
            return word_score(self.grid, self.trie, letters, pos, True, self.temp_blank_letters | self.blank_letters)
        return Err("no letters typed")

    def generate_all_plays(self, tiles):
        plays = SolverState(self.trie, self.grid, tiles).find_all_options()
        valid_plays = []
        for pos, letters, blanks in plays:
            score = word_score(self.grid, self.trie, letters, Position(pos.dir, 14-pos.row, pos.col), True, blanks | self.blank_letters)
            if score.is_ok():
                valid_plays.append(score.unwrap())
        return sorted(valid_plays)

def main():
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()

if __name__ == "__main__":
    main()
