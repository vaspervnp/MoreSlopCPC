"""Headless CPC 6128 harness for MORE SLOP (uses ~/cpcemu).

    from harness import Game
    g = Game()          # boots, RUN"LOADER, waits for the menu
    g.shot("menu.png")
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BUILD = os.path.join(ROOT, "build")
SHOTS = os.path.join(BUILD, "shots")
sys.path.insert(0, os.path.expanduser("~/cpcemu"))

from cpc import CPC  # noqa: E402

KEY_SPACE = 0x20
KEY_LEFT = 0x08
KEY_RIGHT = 0x09
KEY_UP = 0x0B
KEY_DOWN = 0x0A


def symbols():
    sym = {}
    with open(os.path.join(BUILD, "moreslop.sym")) as f:
        for line in f:
            p = line.split()
            if len(p) >= 2 and p[1].startswith("#"):
                sym[p[0].lower()] = int(p[1][1:], 16)
    return sym


class Game:
    def __init__(self, boot=True, max_frames=4000):
        os.makedirs(SHOTS, exist_ok=True)
        self.c = CPC()
        self.sym = symbols()
        if boot:
            self.boot(max_frames)

    def boot(self, max_frames=4000):
        c = self.c
        c.run_frames(150)
        c.insert_disc(os.path.join(BUILD, "moreslop.dsk"))
        c.type_text('RUN"LOADER\n')
        # wait until the menu raster table is live
        for i in range(max_frames // 10):
            c.run_frames(10)
            if self.w("raster_ptr") == self.sym["rast_menu"]:
                self.frames_to_menu = (i + 1) * 10
                c.run_frames(20)
                return
        raise RuntimeError("menu never appeared (pc=%04X)" % c.pc)

    def b(self, name, off=0):
        return self.c.read_ram(self.sym[name] + off, 1)[0]

    def w(self, name):
        d = self.c.read_ram(self.sym[name], 2)
        return d[0] | (d[1] << 8)

    def poke(self, name, value, off=0):
        self.c.write_ram(self.sym[name] + off, bytes([value]))

    def shot(self, name, aspect=True):
        p = os.path.join(SHOTS, name)
        self.c.screenshot(p, aspect=aspect)
        return p

    def hold(self, key, frames):
        self.c.key_down(key)
        self.c.run_frames(frames)
        self.c.key_up(key)

    def tap(self, key, frames=4):
        self.hold(key, frames)
        self.c.run_frames(4)

    def run(self, frames):
        self.c.run_frames(frames)
