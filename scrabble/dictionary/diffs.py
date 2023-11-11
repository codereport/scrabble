# type: ignore

def load(path):
    d = set()
    with open(path) as f:
        for line in f:
            d.add(line.strip().split()[0])
    return d

opsd = load("opsd_4th_ed.txt")
nwl  = load("otcwl_2016.txt")

diff = 0
for w in nwl:
    if w not in opsd and len(w) < 4:
        print(w)
        diff += 1

print(diff)
