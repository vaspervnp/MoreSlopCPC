"""Distribution of game-frame lengths (in 50 Hz video frames)."""
import sys, os, collections
sys.path.insert(0, os.path.dirname(__file__))
from harness import Game, KEY_SPACE, KEY_LEFT, KEY_RIGHT
ep = int(sys.argv[1]); diff = int(sys.argv[2]) if len(sys.argv) > 2 else 2
g = Game(); g.poke("start_ep", ep); g.poke("difficulty", diff)
g.tap(KEY_SPACE); g.run(60); g.tap(KEY_SPACE); g.run(100)
hist = collections.Counter(); last = g.w("game_frames"); t = 0
g.c.key_down(KEY_SPACE)
for i in range(1500):
    if i % 20 == 0:
        g.c.key_up(KEY_LEFT); g.c.key_up(KEY_RIGHT)
        g.c.key_down(KEY_LEFT if (i // 60) % 2 else KEY_RIGHT)
        g.poke("lives", 5)
    g.run(1); t += 1
    f = g.w("game_frames")
    if f != last:
        hist[t] += f - last if f - last > 1 else 0
        hist[t] += 1 if f - last == 1 else 0
        last = f; t = 0
print("ep%d:" % (ep + 1), dict(sorted(hist.items())))
