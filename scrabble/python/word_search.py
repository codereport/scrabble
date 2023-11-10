# type: ignore

d = set()
with open("dictionary_scrabble.txt") as f:
    for line in f:
        d.add(line.strip())

m = dict()
for w in d:
    if len(w) > 7 and len(w) < 10 and (w[-1] != "S" or w[-2] == "S") and w[-3:] != "ING" and w[-2:] != "ED" and w[-2:] != "LY" and w[-2:] != "ER":
        end = w[-4:]
        m[end] = m.get(end, 0) + 1

for i, end in list(reversed(sorted(zip(m.values(), m.keys()))))[:40]:
    print(end, i)

for w in d:
    if len(w) == 8 and w[-4:] == "FISH":
        print(w)
