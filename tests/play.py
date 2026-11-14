"""Start a game and take screenshots while playing (headless)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from harness import Game, KEY_SPACE, KEY_LEFT, KEY_RIGHT

ep = int(sys.argv[1]) if len(sys.argv) > 1 else 0
g = Game()
g.shot("menu.png")
if ep:
    # jump straight to an episode for testing
    g.poke("start_ep", ep)
g.tap(KEY_SPACE)
g.run(80)
g.shot("ep%d_intro.png" % (ep + 1))
g.run(60)
g.tap(KEY_SPACE)
for i in range(12):
    g.c.key_down(KEY_SPACE)
    g.c.key_down(KEY_LEFT if (i // 3) % 2 else KEY_RIGHT)
    g.run(25)
    g.c.key_up(KEY_LEFT); g.c.key_up(KEY_RIGHT)
    if i % 3 == 2:
        g.shot("ep%d_play_%d.png" % (ep + 1, i))
g.c.key_up(KEY_SPACE)
print("state", g.b("state"), "score", g.c.read_ram(g.sym["score"], 3).hex(),
      "lives", g.b("lives"), "quota", g.b("quota_left"), "lag", g.b("lag_count"), "pc %04X" % g.c.pc)
