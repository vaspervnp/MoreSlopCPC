"""Stand-in graphics so the game builds before (or without) the real art.

Sizes match tools/build_assets.py SPRITES; each frame is a simple shape in
the right palette so the engine can be tested.
"""
from PIL import Image, ImageDraw

import cpcgfx as G

SIZES = {
    "themis_m1": ("ep1", 24, 24, 5), "robot_m1": ("ep1", 32, 20, 2),
    "items_ep1": ("ep1", 16, 16, 6), "items_ep2": ("ep2", 16, 16, 6),
    "power_m1": ("ep1", 16, 16, 2), "poof_m1": ("ep1", 16, 16, 3),
    "bolt_m1": ("ep1", 8, 10, 1),
    "themis_m0": ("ep3", 12, 24, 5), "robot_m0": ("ep3", 16, 20, 2),
    "items_ep3": ("ep3", 8, 16, 6), "power_m0": ("ep3", 8, 16, 2),
    "poof_m0": ("ep3", 8, 16, 3), "bolt_m0": ("ep3", 4, 10, 1),
    "bro_float": ("ep3", 12, 32, 1), "bro_walk": ("ep3", 12, 24, 2),
}


def make(name, pal=None, fw=None, fh=None, n=None):
    if pal is None:
        pal, fw, fh, n = SIZES[name]
    rgb = G.pal_rgb(pal)
    img = Image.new("RGBA", (fw * n, fh), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(n):
        x0 = f * fw
        c1 = rgb[1] + (255,)
        c2 = rgb[2] + (255,)
        c3 = rgb[3] + (255,)
        if name.startswith("bolt"):
            d.rectangle([x0, 0, x0 + fw - 1, fh - 1], fill=c3)
            d.rectangle([x0 + fw // 4, 2, x0 + fw - 1 - fw // 4, fh - 3], fill=c1)
        elif name.startswith("poof"):
            r = 3 + f * 2
            cx, cy = x0 + fw // 2, fh // 2
            d.ellipse([cx - r, cy - r, cx + r - 1, cy + r - 1], outline=c3, fill=c2 if f < 2 else None)
        else:
            col = [c1, c2, c3][f % 3]
            d.rectangle([x0 + 1, 1, x0 + fw - 2, fh - 2], fill=col, outline=c3)
            d.line([x0 + 2, 2 + f, x0 + fw - 3, fh - 3], fill=c3)
    return img


def background(ep, mode, pal):
    """Stand-in playfield (320x150 for Mode 1, 160x150 for Mode 0)."""
    p = G.pal_rgb(pal)
    if mode == 0:
        img = Image.new("RGB", (160, 150), p[0])
        d = ImageDraw.Draw(img)
        for y in range(0, 150, 16):
            d.rectangle([0, y, 159, y + 7], fill=p[4])
        d.text((60, 70), "EP%d" % ep, fill=p[5])
    else:
        img = Image.new("RGB", (320, 150), p[0])
        d = ImageDraw.Draw(img)
        for y in range(0, 150, 2):
            for x in range(0, 320, 4):
                if (x // 4 + y // 2) % 9 == 0:
                    img.putpixel((x, y), p[1])
        d.text((150, 70), "EP%d" % ep, fill=p[2])
    return img


def menu():
    img = Image.new("P", (160, 200), 0)
    pal = []
    for c in G.pal_rgb("menu"):
        pal += list(c)
    img.putpalette(pal + [0] * (768 - len(pal)))
    d = ImageDraw.Draw(img)
    for i, y in enumerate(range(8, 64, 4)):
        d.rectangle([10, y, 150, y + 3], fill=1 + (i % 3))
    d.rectangle([2, 118, 157, 185], outline=14)
    return img


def loader():
    img = Image.new("P", (160, 200), 0)
    pal = []
    for c in G.pal_rgb("loader"):
        pal += list(c)
    img.putpalette(pal + [0] * (768 - len(pal)))
    d = ImageDraw.Draw(img)
    for i in range(16):
        d.rectangle([i * 10, 80, i * 10 + 9, 120], fill=i)
    return img
