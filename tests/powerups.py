"""The power-ups you catch: snail, battery, ad blocker, broom."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from harness import Game, KEY_SPACE  # noqa: E402

IT_SIZE = 10
K_SNAIL, K_BATTERY, K_ADBLOCK, K_BROOM = 6, 7, 8, 9
ok = True


def check(name, cond, info=""):
    global ok
    print("%-36s %s %s" % (name, "OK " if cond else "FAIL", info))
    ok &= bool(cond)


def start(ep):
    g = Game()
    g.poke("start_ep", ep)
    g.tap(KEY_SPACE)
    g.run(60)
    g.tap(KEY_SPACE)
    g.run(30)               # let the bolt fired with the card fly off
    assert g.b("state") == 1 and g.b("episode") == ep, (g.b("state"), g.b("episode"))
    return g


def put_item(g, kind, x=None, y=110):
    """One item (slot 0); the other slots are cleared, spawning held off."""
    g.c.write_ram(g.sym["items"], bytes(IT_SIZE * 8))
    if x is None:
        x = g.b("player_x")
    g.c.write_ram(g.sym["items"], bytes([1, x, 0, y, 1, 0, 4, 16, kind, 0]))
    g.poke("spawn_timer", 250)


def items(g):
    raw = g.c.read_ram(g.sym["items"], IT_SIZE * 8)
    return [raw[i * IT_SIZE:(i + 1) * IT_SIZE] for i in range(8) if raw[i * IT_SIZE]]


def fall(g, frames):
    for _ in range(frames // 2):
        g.poke("spawn_timer", 250)
        g.run(2)


for ep in (0, 2):           # a Mode 1 and a Mode 0 episode
    tag = "ep%d" % (ep + 1)
    g = start(ep)

    # zaps pass through, Themis catches it
    put_item(g, K_SNAIL, y=100)
    g.c.key_down(KEY_SPACE)
    fall(g, 16)
    g.c.key_up(KEY_SPACE)
    check(tag + ": zaps pass through a snail", len(items(g)) == 1 and g.b("slow_t") == 0)
    fall(g, 120)
    check(tag + ": Themis catches the snail", not items(g) and g.b("slow_t") > 0, "slow_t %d" % g.b("slow_t"))
    g.shot("powerup_snail_ep%d.png" % (ep + 1))

    # the snail halves the fall speed
    put_item(g, 0, x=10, y=60)
    fall(g, 20)
    slow_dy = items(g)[0][3] - 60
    g.poke("slow_t", 0)
    put_item(g, 0, x=10, y=60)
    fall(g, 20)
    fast_dy = items(g)[0][3] - 60
    check(tag + ": snail halves the fall", 0 < slow_dy * 2 <= fast_dy + 2, "%d vs %d" % (slow_dy, fast_dy))

    # the snail runs out
    g.poke("slow_t", 3)
    put_item(g, 0, x=10, y=60)
    fall(g, 10)
    check(tag + ": the snail runs out", g.b("slow_t") == 0)

    # battery: four bolts in the air
    put_item(g, K_BATTERY, y=140)
    fall(g, 30)
    check(tag + ": battery caught", g.b("turbo_t") > 0, "turbo_t %d" % g.b("turbo_t"))
    g.c.write_ram(g.sym["items"], bytes(IT_SIZE * 8))
    most = 0
    g.c.key_down(KEY_SPACE)
    for _ in range(12):
        g.poke("spawn_timer", 250)
        g.run(2)
        raw = g.c.read_ram(g.sym["bolts"], 6)
        most = max(most, sum(1 for i in range(3) if raw[2 * i + 1]))
    g.c.key_up(KEY_SPACE)
    g.shot("powerup_turbo_ep%d.png" % (ep + 1))
    check(tag + ": turbo puts 3 zaps in the air", most == 3, "max %d" % most)
    g.poke("turbo_t", 0)
    g.run(30)
    most = 0
    g.c.key_down(KEY_SPACE)
    for _ in range(12):
        g.poke("spawn_timer", 250)
        g.run(2)
        raw = g.c.read_ram(g.sym["bolts"], 6)
        most = max(most, sum(1 for i in range(3) if raw[2 * i + 1]))
    g.c.key_up(KEY_SPACE)
    check(tag + ": ...and 2 without it", most == 2, "max %d" % most)
    g.run(30)

    # ad blocker: 3 slop bounce off the shelf
    put_item(g, K_ADBLOCK, y=140)
    fall(g, 30)
    check(tag + ": ad blocker caught", g.b("shield_n") == 3)
    m0 = g.b("misses")
    for n in range(3):
        put_item(g, 0, x=(g.b("player_x") + 30) % 70, y=170)
        fall(g, 30)
    check(tag + ": the shelf bounced 3 slop", g.b("misses") == m0 and g.b("shield_n") == 0,
          "misses %d shield %d" % (g.b("misses"), g.b("shield_n")))
    put_item(g, 0, x=(g.b("player_x") + 30) % 70, y=170)
    fall(g, 30)
    check(tag + ": ...then the 4th lands", g.b("misses") == m0 + 1)

    # broom: the shelf is swept
    g.poke("misses", 2)
    put_item(g, K_BROOM, y=140)
    fall(g, 30)
    check(tag + ": the broom empties the shelf", g.b("misses") == 0)

    # missed one: no harm done
    put_item(g, K_SNAIL, x=(g.b("player_x") + 30) % 70, y=150)
    fall(g, 60)
    check(tag + ": a dropped one costs nothing", not items(g) and g.b("misses") == 0 and g.b("slow_t") == 0)

# they turn up by themselves in a normal game
g = start(0)
seen = set()
for i in range(5000):
    g.run(2)
    g.poke("misses", 0)
    g.poke("quota_left", 50)
    for it in items(g):
        if it[8] >= K_SNAIL:
            seen.add(it[8])
    if len(seen) >= 2 or g.b("state") != 1:
        break
check("power-ups to catch spawn", seen, "kinds %s in %d frames" % (sorted(seen), 2 * i))
print("ALL OK" if ok else "SOME FAILED")
