# Inital code taken from https://github.com/boringcactus/Appel-Jacobson-scrabble/blob/canon/board.py

from collections import defaultdict
from typing import Any

from board import Board, CellCoord, Direction, Letter, Position
from trie import Trie, TrieNode


class SolverState:
    board: Board
    # rack: ???
    # original_rack: ???
    # cross_check_results: ???
    direction: Direction | None
    plays: list[Any]  # This should be better defined: List[Tuple[Position, str, Set[CellCoord]]] or List[Play] as defined in main.py???

    def __init__(self, dictionary: Trie, board: Board, rack): # What is the type of rack?
        self.dictionary = dictionary
        self.board = board
        self.original_rack = rack.copy()
        self.rack = rack
        self.cross_check_results = None
        self.direction = None
        self.plays = []

    def before(self, pos: CellCoord) -> CellCoord:
        row, col = pos
        if self.direction == Direction.ACROSS:
            return row, col - 1
        return row - 1, col

    def after(self, pos: CellCoord) -> CellCoord:
        row, col = pos
        if self.direction == Direction.ACROSS:
            return row, col + 1
        return row + 1, col

    def before_cross(self, pos: CellCoord) -> CellCoord:
        row, col = pos
        if self.direction == Direction.ACROSS:
            return row - 1, col
        return row, col - 1

    def after_cross(self, pos: CellCoord) -> CellCoord:
        row, col = pos
        if self.direction == Direction.ACROSS:
            return row + 1, col
        return row, col + 1

    def legal_move(self, word: str, last_pos: CellCoord) -> None:
        play_pos = last_pos
        word_idx = len(word) - 1
        letters_actually_played = ""
        blanks: set[CellCoord] = set()
        letters_remaining = self.original_rack.copy()
        while word_idx >= 0:
            if self.board.is_empty(play_pos):
                row, col = play_pos
                letter = word[word_idx]
                letters_actually_played += letter
                if letter in letters_remaining:
                    letters_remaining.remove(letter)
                else:
                    letters_remaining.remove(" ")
                    blanks.add((14 - row, col))
            if word_idx == 0:
                assert self.direction is not None # if check_untyped_defs is active, then mypy warns: dir might be None in the construction of Position below
                                                  # we get rid of this warning by adding the assert
                pos = Position(dir=self.direction, row=row, col=col)
                self.plays.append((pos, letters_actually_played[::-1], blanks))
            word_idx -= 1
            play_pos = self.before(play_pos)

    def cross_check_for_display(self, on_rack: bool): # -> ??? Dict[CellCoord, Set[str]] ???
        self.direction = Direction.ACROSS
        a = self.cross_check()
        self.direction = Direction.DOWN
        b = self.cross_check()
        result = defaultdict(set)
        for pos in self.find_anchors():
            result[pos] = a[pos] & b[pos] & set(self.rack) if on_rack else a[pos] & b[pos]
        return result

    def cross_check(self) -> dict[CellCoord, set[Letter]]:
        result: dict[CellCoord, set[Letter]] = dict()
        for pos in self.board.all_positions():
            if self.board.is_filled(pos):
                result[pos] = set()
            letters_before = ""
            scan_pos = pos
            while self.board.is_filled(self.before_cross(scan_pos)):
                scan_pos = self.before_cross(scan_pos)
                letters_before = self.board.tile(scan_pos) + letters_before
            letters_after = ""
            scan_pos = pos
            while self.board.is_filled(self.after_cross(scan_pos)):
                scan_pos = self.after_cross(scan_pos)
                letters_after = letters_after + self.board.tile(scan_pos)
            if len(letters_before) == 0 and len(letters_after) == 0:
                legal_here = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            else:
                legal_here = set()
                for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                    word_formed = letters_before + letter + letters_after
                    if self.dictionary.is_word(word_formed):
                        legal_here.add(letter)
            result[pos] = legal_here
        return result

    def find_anchors(self) -> list[CellCoord]:
        if self.board.is_first_turn():
            return [(7, 7)]
        anchors = []
        for pos in self.board.all_positions():
            empty = self.board.is_empty(pos)
            neighbor_filled = self.board.is_filled(self.before(pos)) or \
                              self.board.is_filled(self.after(pos)) or \
                              self.board.is_filled(self.before_cross(pos)) or \
                              self.board.is_filled(self.after_cross(pos))
            if empty and neighbor_filled:
                anchors.append(pos)
        return anchors

    def before_part(self, partial_word: str, current_node: TrieNode, anchor_pos: CellCoord, limit: int) -> None:
        self.extend_after(partial_word, current_node, anchor_pos, False)
        if limit > 0:
            for next_letter in current_node.children.keys():
                if next_letter in self.rack or " " in self.rack:
                    letter_to_add_back = next_letter if next_letter in self.rack else " "
                    self.rack.remove(letter_to_add_back)
                    self.before_part(
                        partial_word + next_letter,
                        current_node.children[next_letter],
                        anchor_pos,
                        limit - 1
                    )
                    self.rack.append(letter_to_add_back)

    def extend_after(self, partial_word: str, current_node: TrieNode, next_pos: CellCoord, anchor_filled: bool) -> None:
        if (self.board.is_empty(next_pos) or not self.board.in_bounds(next_pos)) and \
            current_node.is_word and anchor_filled:
            self.legal_move(partial_word, self.before(next_pos))
        if self.board.in_bounds(next_pos):
            if self.board.is_empty(next_pos):
                for next_letter in current_node.children.keys():
                    assert self.cross_check_results is not None  # make mypy happy about the next line
                    if (next_letter in self.rack or " " in self.rack) and next_letter in self.cross_check_results[next_pos]:
                        letter_to_add_back = next_letter if next_letter in self.rack else " "
                        self.rack.remove(letter_to_add_back)
                        self.extend_after(
                            partial_word + next_letter,
                            current_node.children[next_letter],
                            self.after(next_pos),
                            True
                        )
                        self.rack.append(letter_to_add_back)
            else:
                existing_letter = self.board.tile(next_pos)
                if existing_letter in current_node.children.keys():
                    self.extend_after(
                        partial_word + existing_letter,
                        current_node.children[existing_letter],
                        self.after(next_pos),
                        True
                    )

    def find_all_options(self):
        for direction in Direction:
            self.direction = direction
            anchors = self.find_anchors()
            self.cross_check_results = self.cross_check()
            for anchor_pos in anchors:
                if self.board.is_filled(self.before(anchor_pos)):
                    scan_pos = self.before(anchor_pos)
                    partial_word = self.board.tile(scan_pos)
                    while self.board.is_filled(self.before(scan_pos)):
                        scan_pos = self.before(scan_pos)
                        partial_word = self.board.tile(scan_pos) + partial_word
                    pw_node = self.dictionary.lookup(partial_word)
                    if pw_node is not None:
                        self.extend_after(
                            partial_word,
                            pw_node,
                            anchor_pos,
                            False
                        )
                else:
                    limit = 0
                    scan_pos = anchor_pos
                    while self.board.is_empty(self.before(scan_pos)) and self.before(scan_pos) not in anchors:
                        limit = limit + 1
                        scan_pos = self.before(scan_pos)
                    self.before_part("", self.dictionary.root, anchor_pos, limit)
        return self.plays
