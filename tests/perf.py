"""Measure late frames (25 fps target) per episode while playing hard."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from harness import Game, KEY_SPACE, KEY_LEFT, KEY_RIGHT

ep = int(sys.argv[1]) if len(sys.argv) > 1 else 0
diff = int(sys.argv[2]) if len(sys.argv) > 2 else 2
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
g = Game()
if seed:
    g.c.write_ram(g.sym["seed"], bytes([seed & 255, 0x5A]))
g.poke("start_ep", ep)
g.poke("difficulty", diff)
g.tap(KEY_SPACE)
g.run(60)
g.tap(KEY_SPACE)
g.run(40)
g.poke("lag_count", 0)
f0 = g.w("game_frames")
worst = 0
for i in range(40):
    g.c.key_down(KEY_SPACE)
    g.c.key_down(KEY_LEFT if (i // 4) % 2 else KEY_RIGHT)
    g.run(25)
    g.c.key_up(KEY_LEFT); g.c.key_up(KEY_RIGHT)
    g.poke("lives", 5)
g.c.key_up(KEY_SPACE)
fr = g.w("game_frames") - f0
print("seed %d ep%d diff%d:" % (seed,) + "" if False else "seed %d " % seed + "ep%d diff%d: %d game frames in 1000 video frames (ideal 500), late %d, state %d"
      % (ep + 1, diff, fr, g.b("lag_count"), g.b("state")))
