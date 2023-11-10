
from collections import Counter
from math import prod

from termcolor import colored


def dictionary_from_file(file_name):
    d = set()
    with open(file_name) as f:
        for line in f:
            d.add(line.strip().upper())
    return d

scrabble_dict = dictionary_from_file("dictionary_scrabble.txt")
wordle_dict   = dictionary_from_file("dictionary_wordle.txt")

def wordle(guesses, results):
    possible_words = []
    for w in wordle_dict:
        possible = True
        if len(w) == 5:
            for guess, result in zip(guesses, results):
                ww = w

                for i, (g, r) in enumerate(zip(guess,result)):
                    if r == "G":
                        if w[i] != g:
                            possible = False
                        else:
                            ww = ww.replace(g, "", 1)
                    if r == "Y" and (g not in w or g == w[i]):
                        possible = False
                    if r == "." and g in ww:
                        possible = False
                if not possible:
                    break
            if possible:
                possible_words.append(w)
    return possible_words

def list_pad(lst, n):
    return lst + ["-"] * max(0, n - len(lst))

def int_pad(i, n):
    s = str(i)
    l = (n - len(s)) // 2
    r = n - len(s) - l
    return " " * l + s + " " * r

def top_words(words, n):
    freq = [Counter(letters) for letters in zip(*words)]
    scored_words = [(prod(freq[i][l] if w.count(l) == 1 else 1 for i, l in enumerate(w)), w) for w in words]
    return [w for _, w in sorted(scored_words)[-n:][::-1]]

def top_words2(words, n):
    freq = Counter("".join(words))
    scored_words = [(prod(freq[l] if w.count(l) == 1 else 1 for l in w), w) for w in words]
    return [w for _, w in sorted(scored_words)[-n:][::-1]]

def top_words3(words, n):
    freq = [Counter(letters) for letters in zip(*words)]
    freq2 = Counter("".join(words))
    scored_words = [(prod(freq2[l] if w.count(l) == 1 else 1 for l in w),
                     prod(freq[i][l] if w.count(l) == 1 else 1 for i, l in enumerate(w)),
                     w) for w in words]
    return [w for _, _, w in sorted(scored_words)[-n:][::-1]]

def print_wordle_table(headers, columns):
    line_break = "     +" + ("-" * (len(headers) * 8 - 1)) + "+"
    print(line_break)
    print("     | " + " | ".join(headers) + " |")
    print(line_break)
    for row in columns[:-1]:
        print("     | ", end = "")
        for word in row:
            if word in wordle_dict:
                print(colored(word, "green", attrs=["bold"]), end = "")
            elif word != "-":
                print(colored(word, "red", attrs=["bold"]), end = "")
            else:
                print("  " + word + "  ", end = "")
            print(" | ", end = "")
        print()
    print(line_break)
    print("     | ", end = "")
    for word in columns[-1]:
        print(colored(int_pad(word, 5), "cyan", attrs=["bold"]), end = "")
        print(" | ", end = "")
    print()
    print(line_break)
    print()

def wordle_table(guesses, results):
    table = []
    for end in range(1, len(guesses) + 1):
        possible_words = wordle(guesses[:end], results[:end])
        table.append(list_pad(top_words3(possible_words, 10), 10) + [len(possible_words)])

    print_wordle_table(guesses, list(zip(*table)))

print()
wordle_table(["AROSE","PAINT","DUCAL"], ["Y....", ".Y...","..YY."])
