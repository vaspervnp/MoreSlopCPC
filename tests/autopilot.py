"""A computer player for MORE SLOP (used for the gameplay video).

It reads the item table from RAM and steers Themis like a decent but human
player: it chases the lowest piece of slop, fires when the bolt would line
up, takes a moment to react to new targets and now and then gets distracted.
Only the keyboard is used - no pokes.
"""
import random

from harness import KEY_SPACE, KEY_LEFT, KEY_RIGHT

IT_SIZE, MAX_ITEMS = 10, 8
BR_SIZE, MAX_BROS = 5, 2
PLAYER_W = 6
CATCH, BATTERY = 6, 7                  # item kinds from here on are caught by walking under them


class Autopilot:
    def __init__(self, g, seed=7, skill=0.9):
        self.g = g
        self.rnd = random.Random(seed)
        self.skill = skill          # chance per decision to act correctly
        self.target = None
        self.react = 0              # frames left before reacting to a new target
        self.daydream = 0           # frames of doing nothing useful
        self.keys = set()

    def _press(self, want):
        c = self.g.c
        for k in (KEY_LEFT, KEY_RIGHT, KEY_SPACE):
            if k in want and k not in self.keys:
                c.key_down(k)
            elif k not in want and k in self.keys:
                c.key_up(k)
        self.keys = set(want)

    def release(self):
        self._press(set())

    def items(self):
        g = self.g
        raw = g.c.read_ram(g.sym["items"], IT_SIZE * MAX_ITEMS)
        out = []
        for i in range(MAX_ITEMS):
            r = raw[i * IT_SIZE:(i + 1) * IT_SIZE]
            if r[0]:
                out.append(dict(kind=r[8], x=r[1], y=r[3], dx=r[4] if r[4] < 128 else r[4] - 256,
                                w=r[6], h=r[7]))
        return out

    def bros(self):
        g = self.g
        raw = g.c.read_ram(g.sym["bros"], BR_SIZE * MAX_BROS)
        return [dict(st=raw[i * BR_SIZE], x=raw[i * BR_SIZE + 1], y=raw[i * BR_SIZE + 3])
                for i in range(MAX_BROS) if raw[i * BR_SIZE] in (1, 2)]

    def step(self):
        """Decide the keys for the next game frame."""
        g = self.g
        if g.b("state") != 1:
            self.release()
            return
        px = g.b("player_x")
        if self.daydream:
            self.daydream -= 1
            self._press({KEY_SPACE} if self.daydream % 6 < 3 else set())
            return
        if self.rnd.random() > self.skill and self.rnd.random() < 0.02:
            self.daydream = self.rnd.randint(8, 30)
        its = self.items()
        tgt = None
        if its:
            # lowest slop first; power-ups only when nothing is close to the shelf
            # (decoys - kind 5 - are left alone; kinds 6+ are caught, not zapped)
            slop = [i for i in its if i["kind"] < 3]
            power = [i for i in its if i["kind"] in (3, 4)]
            catch = sorted((i for i in its if i["kind"] >= CATCH), key=lambda i: -i["y"])
            if g.b("boss_on"):      # in the boss fight only a battery is worth the walk
                catch = [i for i in catch if i["kind"] == BATTERY]
            pool = sorted(slop, key=lambda i: -i["y"])
            if catch and catch[0]["y"] > 90 and (not pool or pool[0]["y"] < 150):
                c = catch[0]
                want = c["x"] + c["w"] // 2 - PLAYER_W // 2
                keys = set()
                if want < px - 1:
                    keys.add(KEY_LEFT)
                elif want > px + 1:
                    keys.add(KEY_RIGHT)
                if pool and abs(pool[0]["x"] + pool[0]["w"] // 2 - px - 3) < 3:
                    keys.add(KEY_SPACE)     # zaps fly through it anyway
                self._press(keys)
                return
            if power and (not pool or pool[0]["y"] < 120):
                pool = power + pool
            tgt = pool[0] if pool else None
        bros = self.bros()
        if bros and (tgt is None or tgt["y"] < 110):
            b = min(bros, key=lambda b: abs(b["x"] - px))
            tgt = dict(x=b["x"], w=6, y=b["y"], dx=0, kind=9)
        if g.b("boss_on") and (tgt is None or tgt["y"] < 145):
            # the SlopBot moves 2 bytes a frame and a bolt needs ~10 frames
            # to reach it: aim 20 bytes ahead (bouncing off the edges like
            # the robot does) and keep firing
            dx = 2 if g.b("robot_dx") < 128 else -2
            x = g.b("robot_x") + dx * 10
            x = -x if x < 0 else (144 - x if x > 72 else x)
            keys = {KEY_SPACE}
            if x + 1 < px:
                keys.add(KEY_LEFT)
            elif x > px:
                keys.add(KEY_RIGHT)
            self._press(keys)
            return
        if tgt is None:
            self._press(set())
            return
        key = (tgt["kind"], tgt["x"] // 8)
        if key != self.target:
            self.target = key
            self.react = self.rnd.randint(1, 4)
        if self.react:
            self.react -= 1
            self._press(set())
            return
        # aim the bolt (x+2 .. x+3) at the middle of the target, leading a little
        cx = tgt["x"] + tgt["w"] // 2 + tgt["dx"] * 2
        want = cx - 3 + self.rnd.choice((0, 0, 0, -1, 1))
        want = max(0, min(80 - PLAYER_W, want))
        keys = set()
        if want < px - 1:
            keys.add(KEY_LEFT)
        elif want > px + 1:
            keys.add(KEY_RIGHT)
        bx = px + 2
        if tgt["x"] - 1 <= bx + 1 and bx <= tgt["x"] + tgt["w"]:
            keys.add(KEY_SPACE)
        self._press(keys)
