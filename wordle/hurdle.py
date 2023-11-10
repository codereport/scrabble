
import random

from rich.console import Console


def dictionary_from_file(file_name):
    d = set()
    with open(file_name) as f:
        for line in f:
            d.add(line.strip().upper())
    return d

scrabble_dict = dictionary_from_file("dictionary_scrabble.txt")

def start_game():
    print("Enter number of letters: ", end="")
    n = int(input())
    print("Enter number of guesses: ", end="")
    g = int(input())

    words = [w for w in scrabble_dict if len(w) == n]

    console = Console()

    while True:
        print()
        target = words[int(random.random() * len(words))]
        for _ in range(g):
            print("Guess: ",end="")
            guess = input()
            print("\b\b\b\b\b\b\b",end="")
            if guess == target:
                break

            colors = [0] * n
            remaining = ""

            for i, (a, b) in enumerate(zip(target, guess)):
                if a == b:
                    colors[i] = 1
                else:
                    remaining += a

            for i, (a, b) in enumerate(zip(target, guess)):
                if a != b and b in remaining:
                    colors[i] = 2
                    remaining = remaining.replace(b, "", 1)

            for a, b in zip(guess, colors):
                if b == 0:
                    print(a, end="")
                if b == 1:
                    console.print(a, style="bold black on green", end="")
                if b == 2:
                    console.print(a, style="bold black on yellow", end="")
            print()
        print(target)

start_game()
