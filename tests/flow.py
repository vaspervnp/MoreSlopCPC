"""Whole-game flow: waves, episode changes, life loss, game over, menu."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from harness import Game, KEY_SPACE, KEY_LEFT, KEY_RIGHT

ok = True
def check(name, cond, info=""):
    global ok
    print("%-28s %s %s" % (name, "OK " if cond else "FAIL", info))
    ok &= bool(cond)

g = Game()
# difficulty via keys: '3' then '1' then down -> 2nd
g.tap(ord('3')); check("menu: key 3 -> SINGULARITY", g.b("difficulty") == 2)
g.tap(ord('1')); check("menu: key 1 -> TOUCH GRASS", g.b("difficulty") == 0)
g.tap(0x0A); g.run(4); check("menu: down -> TERMINALLY", g.b("difficulty") == 1)
g.tap(KEY_SPACE); g.run(80)
check("game starts in episode 1", g.b("state") == 0 and g.b("episode") == 0)
check("normal: 3 lives", g.b("lives") == 3)
g.tap(KEY_SPACE); g.run(10)
check("intro card closes on fire", g.b("state") == 1)

def clear_wave():
    g.poke("quota_left", 1)
    for i in range(1200):
        g.c.key_down(KEY_SPACE)
        if i % 12 == 0:
            g.c.key_up(KEY_LEFT); g.c.key_up(KEY_RIGHT)
            # walk under the robot
            g.c.key_down(KEY_LEFT if g.b("player_x") > g.b("robot_x") + 1 else KEY_RIGHT)
        g.run(2)
        g.poke("misses", 0)
        if g.b("state") == 2:
            break
    g.c.key_up(KEY_SPACE); g.c.key_up(KEY_LEFT); g.c.key_up(KEY_RIGHT)
    return g.b("state") == 2

NUM_EPS = 10
for ep in range(NUM_EPS):
    for wv in range(3):
        cleared = clear_wave()
        check("ep%d wave%d cleared" % (ep + 1, wv + 1), cleared, "score %s" % g.c.read_ram(g.sym["score"], 3).hex())
        if ep == 0 and wv == 0:
            g.run(30); g.shot("flow_clear_card.png")
        g.run(200)
        if wv < 2:
            check("  -> next wave", g.b("wave") == wv + 1 and g.b("episode") == ep, "state %d" % g.b("state"))
            g.run(10)
    if ep < NUM_EPS - 1:
        for t in range(200):
            if g.b("state") == 0:
                break
            g.run(1)
        if ep == 0:
            print("  (episode change finished %d frames later)" % t)
        check("  -> episode %d" % (ep + 2), g.b("episode") == ep + 1 and g.b("state") == 0, "ep %d state %d" % (g.b("episode"), g.b("state")))
        g.run(60); g.shot("flow_ep%d_card.png" % (ep + 2))
        g.tap(KEY_SPACE); g.run(10)
check("victory card after episode 10", g.b("state") == 5)
g.shot("flow_victory.png")
g.tap(KEY_SPACE); g.run(150)
check("loop 2 starts at episode 1", g.b("loop_n") == 1 and g.b("episode") == 0)
g.tap(KEY_SPACE); g.run(20)
# lose every life: let slop hit the shelf
g.poke("lives", 1); g.poke("misses", 2)
g.c.write_ram(g.sym["score"], bytes([0x01, 0x23, 0x45]))
for i in range(600):
    g.run(5)
    if g.b("state") == 4:
        break
check("game over after the last life", g.b("state") == 4)
g.run(100); g.shot("flow_gameover.png")
g.tap(KEY_SPACE); g.run(120)
check("back to the menu", g.w("raster_ptr") == g.sym["rast_menu"])
hi = g.c.read_ram(g.sym["hiscore"], 3).hex()
check("hi-score updated", hi == "012345", hi)
g.shot("flow_menu_after.png")
print("ALL OK" if ok else "SOME FAILED")
