"""Sample the program counter while playing to see where the time goes."""
import sys, os, collections
sys.path.insert(0, os.path.dirname(__file__))
from harness import Game, KEY_SPACE, KEY_LEFT, KEY_RIGHT
ep = int(sys.argv[1]) if len(sys.argv) > 1 else 2
g = Game(); g.poke("start_ep", ep); g.poke("difficulty", 2)
g.tap(KEY_SPACE); g.run(60); g.tap(KEY_SPACE); g.run(200)
labs = sorted((v, k) for k, v in g.sym.items() if v < 0x4000 and not k.startswith(('@',)))
import bisect
keys = [v for v, k in labs]
# only "routine" labels: those that are called or jumped to (heuristic: no underscore-number suffix)
hist = collections.Counter()
g.c.key_down(KEY_SPACE)
for i in range(60):
    g.c.key_down(KEY_LEFT if (i // 8) % 2 else KEY_RIGHT)
    for _ in range(312 * 2 // 4):
        g.c.run_us(256)
        pc = g.c.pc
        j = bisect.bisect_right(keys, pc) - 1
        hist[labs[j][1] if j >= 0 else "?"] += 1
    g.c.key_up(KEY_LEFT); g.c.key_up(KEY_RIGHT)
    g.poke("lives", 5)
tot = sum(hist.values())
for k, n in hist.most_common(25):
    print("%5.1f%% %s" % (100.0 * n / tot, k))
