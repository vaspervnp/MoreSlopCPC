"""The episode mechanics: decoys, splitting slop, the bass drop, the boss."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from harness import Game, KEY_SPACE  # noqa: E402

IT_SIZE = 10
ok = True


def check(name, cond, info=""):
    global ok
    print("%-34s %s %s" % (name, "OK " if cond else "FAIL", info))
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


def put_item(g, kind, y=110, anim=0):
    """An item right above Themis (slot 0); the other slots are cleared."""
    g.c.write_ram(g.sym["items"], bytes(IT_SIZE * 8))
    px = g.b("player_x")
    g.c.write_ram(g.sym["items"], bytes([1, px, 0, y, 1, 0, 4, 16, kind, anim]))
    g.poke("spawn_timer", 250)


def items(g):
    raw = g.c.read_ram(g.sym["items"], IT_SIZE * 8)
    return [raw[i * IT_SIZE:(i + 1) * IT_SIZE] for i in range(8) if raw[i * IT_SIZE]]


def zap(g, frames=12):
    g.c.key_down(KEY_SPACE)
    g.run(frames)
    g.c.key_up(KEY_SPACE)


# episode 4: the deepfake of Themis flips the controls
g = start(3)
put_item(g, 5)
zap(g)
check("ep4: zapping the deepfake flips", g.b("player_rev") > 0, "rev %d" % g.b("player_rev"))
x0 = g.b("player_x")
g.c.key_down(0x08)          # LEFT
g.run(16)
g.c.key_up(0x08)
check("ep4: ...so left walks right", g.b("player_x") > x0, "%d -> %d" % (x0, g.b("player_x")))

# episode 6: zapping Gary counts as slop on the shelf
g = start(5)
m0 = g.b("misses")
put_item(g, 5)
zap(g)
check("ep6: zapping Gary costs a shelf slot", g.b("misses") == m0 + 1, "misses %d" % g.b("misses"))

# episode 5: slop splits (half the time) into two halves that don't split again
g = start(4)
split = False
for attempt in range(12):
    put_item(g, 0)
    q = g.b("quota_left")
    zap(g, 2)               # one bolt only
    g.run(16)
    its = items(g)
    if len(its) == 2:
        split = True
        check("ep5: split keeps the quota", g.b("quota_left") == q, "quota %d" % g.b("quota_left"))
        check("ep5: halves are marked", all(i[9] & 1 for i in its))
        break
    g.run(20)
check("ep5: slop split in two", split, "after %d tries" % (attempt + 1))

# episode 9: the bass drops every 10 seconds
g = start(8)
dropped = 0
for i in range(400):
    g.run(2)
    g.poke("misses", 0)
    if g.b("drop_timer"):
        dropped = i
        break
check("ep9: the bass drops", dropped > 0, "after %d game frames" % dropped)

# episode 10: the boss wakes up when the last wave's quota is done
g = start(9)
g.poke("wave", 2)
g.poke("quota_left", 1)
put_item(g, 0)
zap(g, 2)
g.run(16)
check("ep10: boss fight starts", g.b("boss_on") == 1 and g.b("quota_left") == 12,
      "boss %d hp %d" % (g.b("boss_on"), g.b("quota_left")))
for i in range(1500):
    g.c.key_down(KEY_SPACE)
    rx, px = g.b("robot_x"), g.b("player_x")
    g.c.key_up(0x08)
    g.c.key_up(0x09)
    if px + 3 < rx + 4:
        g.c.key_down(0x09)
    elif px + 3 > rx + 4:
        g.c.key_down(0x08)
    g.run(2)
    g.poke("misses", 0)
    if g.b("state") == 2:
        break
g.c.key_up(KEY_SPACE)
check("ep10: zapping the SlopBot clears the wave", g.b("state") == 2 and g.b("boss_on") == 0,
      "state %d after %d frames" % (g.b("state"), 2 * i))
g.shot("mech_boss_down.png")
print("ALL OK" if ok else "SOME FAILED")
