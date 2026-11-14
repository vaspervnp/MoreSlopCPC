"""MORE SLOP sprite models (run inside Blender: exec this file, then call).

Every sprite is modelled in pixel units in a box the size of the Mode 1
sprite (Mode 0 versions use the same models, rendered with 2:1 pixels).
Colour schemes map roles (skin, cape...) to (lit, shadow) firmware colours.
"""
import math
import sys
import importlib

sys.path.insert(0, r"\\wsl.localhost\Ubuntu\home\vasilhs\repos\MoreSlopCPC\tools\blender")
import msblend as B  # noqa: E402
importlib.reload(B)

# firmware colours of each episode's pens
EP1 = dict(bg=1, c=20, m=8, w=26)          # dark blue, cyan, magenta, white
EP3 = dict(k=0, c=20, m=8, w=26, b=1, mv=5, r=3, o=15, y=24, pk=16, g=18, dg=9, sky=11, gr=13, br=6, pu=7)

THEMIS_M1 = dict(skin=(26, 20), hair=(8, 8), shirt=(20, 1), cape=(8, 1), pants=(20, 1),
                 shoe=(26, 26), dark=(1, 1), zap=(26, 20), spark=(26, 26), star=(26, 26))
THEMIS_M0 = dict(skin=(16, 16), hair=(15, 3), shirt=(26, 13), cape=(6, 3), pants=(11, 1),
                 shoe=(13, 13), dark=(0, 0), zap=(24, 15), spark=(24, 24), star=(24, 24))


def M(pal, role):
    lit, sh = pal[role]
    return B.toon(lit, sh)


# ---------------------------------------------------------------- Themis
def themis(sc, pal, pose):
    """24x24 hero. pose: idle, walk1, walk2, zap, dizzy"""
    tilt = 12 if pose == "dizzy" else 0
    lstep = {"walk1": 1.5, "walk2": -1.5}.get(pose, 0)
    # legs and shoes
    for side, sx in ((-1, 8.5), (1, 12.5)):
        lift = max(0, lstep * side)
        B.box(sc, sx, 2 + lift, 3, 6, M(pal, "pants"), d=3, name="leg")
        B.box(sc, sx - (1 if side < 0 else 0), 0 + lift, 4, 2.2, M(pal, "shoe"), d=4, name="shoe")
    # cape behind the body
    B.poly(sc, [(6, 3), (18, 3), (16.5, 15), (7.5, 15)], M(pal, "cape"), d=1, y=3, name="cape")
    # torso
    B.box(sc, 7.5, 7.5, 9, 7.5, M(pal, "shirt"), d=5, name="torso")
    B.box(sc, 7.5, 7.5, 9, 1.2, M(pal, "dark"), d=5.2, name="belt")
    # head
    hx, hz = 12 + (1 if pose == "dizzy" else 0), 18.5
    head = B.ball(sc, hx, hz, 4.6, M(pal, "skin"), name="head")
    head.rotation_euler = (0, math.radians(tilt), 0)
    # hair: messy tuft
    B.ball(sc, hx, hz + 2.8, 4.2, M(pal, "hair"), sz=0.55, y=0.6, name="hair")
    B.poly(sc, [(hx - 1, hz + 4), (hx + 1.5, hz + 7.2), (hx + 2.5, hz + 3.5)], M(pal, "hair"), d=2, y=-2,
           name="tuft")
    # glasses + grin
    if pose == "dizzy":
        for gx in (hx - 2.6, hx + 1.0):
            B.poly(sc, [(gx, hz), (gx + 1.6, hz + 1.6), (gx + 1.6, hz + 0.8), (gx + 0.8, hz)],
                   M(pal, "dark"), d=1, y=-5, name="xeye")
        B.box(sc, hx - 1, hz - 2.6, 2, 1.4, M(pal, "dark"), d=1, y=-4.5, name="mouth")
    else:
        B.box(sc, hx - 3.6, hz + 0.2, 3, 2, M(pal, "dark"), d=1, y=-4.4, name="glassL")
        B.box(sc, hx + 0.6, hz + 0.2, 3, 2, M(pal, "dark"), d=1, y=-4.4, name="glassR")
        B.box(sc, hx - 2.2, hz - 2.4, 4.4, 1, M(pal, "dark"), d=1, y=-4.4, name="grin")
    # arms + zapper
    swing = {"walk1": -1, "walk2": 1}.get(pose, 0)
    B.box(sc, 5.5, 8.5 + swing, 2, 5.5, M(pal, "shirt"), d=2.5, name="armL")
    B.ball(sc, 6.5, 8 + swing, 1.3, M(pal, "skin"), name="handL")
    if pose == "zap":
        B.box(sc, 16.5, 13, 2, 6, M(pal, "shirt"), d=2.5, name="armR")
        B.ball(sc, 17.5, 19.5, 1.3, M(pal, "skin"), name="handR")
        B.box(sc, 16.6, 19.5, 1.8, 4, M(pal, "zap"), d=2, name="zapper")
        B.poly(sc, [(17.5, 24), (15.5, 22), (19.5, 22)], M(pal, "spark"), d=1, y=-3, name="spark")
    else:
        B.box(sc, 16.5, 8.5 - swing, 2, 5.5, M(pal, "shirt"), d=2.5, name="armR")
        B.ball(sc, 17.5, 8 - swing, 1.3, M(pal, "skin"), name="handR")
        B.box(sc, 18, 6.5 - swing, 4, 1.8, M(pal, "zap"), d=2, name="zapper")
        B.box(sc, 21.5, 7 - swing, 1.2, 0.8, M(pal, "spark"), d=2.2, name="tip")
    if pose == "dizzy":
        for (sx, sz) in ((5, 22), (19, 23), (12, 24)):
            B.poly(sc, [(sx, sz + 1), (sx + 0.4, sz + 0.3), (sx + 1, sz), (sx + 0.4, sz - 0.3),
                        (sx, sz - 1), (sx - 0.4, sz - 0.3), (sx - 1, sz), (sx - 0.4, sz + 0.3)],
                   M(pal, "star"), d=1, y=-6, name="star")


def render_themis(mode):
    poses = ["idle", "walk1", "walk2", "zap", "dizzy"]
    pal = THEMIS_M1 if mode == 1 else THEMIS_M0
    paths = []
    for p in poses:
        sc = B.scene("themis_m%d_%s" % (mode, p), 24 if mode == 1 else 12, 24, 1.0 if mode == 1 else 2.0)
        themis(sc, pal, p)
        paths.append(B.render(sc, "themis_m%d/%s.png" % (mode, p)))
    return paths


# ---------------------------------------------------------------- SlopBot
ROBOT_M1 = dict(body=(20, 1), screen=(1, 1), eye=(8, 8), slot=(1, 1), glow=(26, 26), ant=(8, 8),
                jet=(26, 20))
ROBOT_M0 = dict(body=(13, 4), screen=(0, 0), eye=(10, 10), slot=(0, 0), glow=(8, 8), ant=(14, 6),
                jet=(7, 6))
# the Mode 0 robot uses ep3 pen roles via firmware numbers below
ROBOT_M0 = dict(body=(26, 13), screen=(0, 0), eye=(18, 18), slot=(0, 0), glow=(24, 24), ant=(6, 3),
                jet=(15, 6))


def robot(sc, pal, printing):
    B.box(sc, 4, 4, 24, 13, M(pal, "body"), d=8, name="body")
    B.ball(sc, 4.5, 10.5, 3.2, M(pal, "body"), sx=0.6, name="earL")
    B.ball(sc, 27.5, 10.5, 3.2, M(pal, "body"), sx=0.6, name="earR")
    B.box(sc, 8, 7, 16, 8, M(pal, "screen"), d=8.4, name="screen")
    if printing:
        for ex in (10.5, 18.5):
            B.poly(sc, [(ex, 11), (ex + 1.5, 13), (ex + 3, 11), (ex + 2.2, 11), (ex + 1.5, 12),
                        (ex + 0.8, 11)], M(pal, "eye"), d=1, y=-5, name="eye^")
        B.box(sc, 13, 8, 6, 2, M(pal, "eye"), d=1, y=-5, name="mouthO")
    else:
        for ex in (10.5, 18.5):
            B.box(sc, ex, 10.5, 3, 3, M(pal, "eye"), d=1, y=-5, name="eye")
        B.box(sc, 12, 8.5, 8, 1, M(pal, "eye"), d=1, y=-5, name="smile")
    B.box(sc, 10, 1.5, 12, 2.5, M(pal, "glow" if printing else "slot"), d=8.4, name="slot")
    B.box(sc, 15.5, 17, 1, 2, M(pal, "ant"), d=1, name="antenna")
    B.ball(sc, 16, 19, 1.4, M(pal, "glow" if printing else "ant"), name="antball")
    for jx in (6, 23):
        B.box(sc, jx, 2, 3, 2, M(pal, "jet"), d=3, name="jet")


def render_robot(mode):
    out = []
    for f, printing in enumerate((False, True)):
        sc = B.scene("robot_m%d_%d" % (mode, f), 32 if mode == 1 else 16, 20, 1.0 if mode == 1 else 2.0)
        robot(sc, ROBOT_M1 if mode == 1 else ROBOT_M0, printing)
        out.append(B.render(sc, "robot_m%d/%d.png" % (mode, f)))
    return out


# ------------------------------------------------------------ slop, ep 1
def portrait(sc, f, c):
    B.box(sc, 1, 1, 14, 14, B.toon(c["m"], c["bg"]), d=2, name="frame")
    B.box(sc, 3, 3, 10, 10, B.flat(c["w"]), d=2.2, name="canvas")
    drip = 1.5 if f else 0
    B.ball(sc, 8, 8.5 - drip / 2, 3.6, B.toon(c["c"], c["bg"]), sz=1.1 + drip / 6, y=-1.5, name="face")
    B.box(sc, 5.6, 9.5, 1.6, 1.6, B.flat(c["bg"]), d=1, y=-5, name="eyeL")
    B.box(sc, 9.0, 8.0 + f, 2.2, 2.2, B.flat(c["bg"]), d=1, y=-5, name="eyeR")
    B.poly(sc, [(5.5, 6), (7, 5.2 - f), (8.5, 6), (10, 5.2 - f), (10.5, 6.2), (5.5, 6.8)],
           B.flat(c["m"]), d=1, y=-5, name="mouth")
    if f:
        B.box(sc, 6, 2.2, 1, 2.5, B.flat(c["c"]), d=1, y=-4, name="drip1")
        B.box(sc, 9.5, 1.5, 1, 3, B.flat(c["c"]), d=1, y=-4, name="drip2")


def cat3(sc, f, c):
    B.ball(sc, 8, 5, 5.5, B.toon(c["c"], c["bg"]), sz=0.6, name="body")
    B.box(sc, 3, 1, 1.5, 3, B.flat(c["c"]), d=1, name="legL")
    B.box(sc, 11.5, 1, 1.5, 3, B.flat(c["c"]), d=1, name="legR")
    B.poly(sc, [(13, 5), (15.5, 9), (14, 9.5), (12, 6)], B.flat(c["m"]), d=1, name="tail")
    for i, hx in enumerate((3.5, 8, 12.5)):
        hz = 10.5 + (1 if (i + f) % 2 else 0)
        B.ball(sc, hx, hz, 2.6, B.toon(c["w"], c["c"]), name="head")
        B.poly(sc, [(hx - 2.4, hz + 1), (hx - 1.8, hz + 3.6), (hx - 0.6, hz + 1.8)], B.flat(c["m"]), d=1,
               y=-3, name="earL")
        B.poly(sc, [(hx + 2.4, hz + 1), (hx + 1.8, hz + 3.6), (hx + 0.6, hz + 1.8)], B.flat(c["m"]), d=1,
               y=-3, name="earR")
        B.box(sc, hx - 1.5, hz, 1, 1, B.flat(c["bg"]), d=1, y=-3, name="eye")
        B.box(sc, hx + 0.5, hz, 1, 1, B.flat(c["bg"]), d=1, y=-3, name="eye")


def hand6(sc, f, c):
    """A hand with SIX fingers, spread like a rake."""
    skin = B.toon(c["w"], c["c"])
    B.box(sc, 2, 2.5, 11, 5.5, skin, d=3, name="palm")
    B.box(sc, 5, 0, 6, 2.5, B.flat(c["m"]), d=3.5, name="cuff")
    for i in range(6):
        L = (5, 6.5, 7, 7, 6.5, 5)[i] + (0.8 if (i + f) % 2 else 0)
        B.box(sc, 2.05 + i * 2, 7.5, 0.9, L, skin, d=1.5, name="finger")
        B.box(sc, 2.05 + i * 2, 7.5 + L - 1, 0.9, 1, B.flat(c["m"]), d=1.7, name="nail")
    B.box(sc, 0.5, 3.5, 3, 1.4, skin, d=1.5, rot=-30, name="thumb?")


# ------------------------------------------------------------ slop, ep 2
EP2 = dict(k=0, o=15, r=3, y=24)


def newspaper(sc, f, c):
    B.box(sc, 1.5, 1.5, 13, 13, B.toon(c["y"], c["o"]), d=1, rot=(8 if f else -4), name="paper")
    for i in range(4):
        B.box(sc, 3.5, 11 - i * 2.4, 7 if i else 9, 1, B.flat(c["r"]), d=1.2, y=-1,
              rot=(8 if f else -4), name="line")
    B.box(sc, 11.5, 4, 1.6, 6, B.flat(c["r"]), d=1.2, y=-1.5, name="bang")
    B.box(sc, 11.5, 2, 1.6, 1.4, B.flat(c["r"]), d=1.2, y=-1.5, name="dot")


def plane(sc, f, c):
    pts = [(1, 9), (15, 13), (7, 3)] if f == 0 else [(15, 9), (1, 13), (9, 3)]
    B.poly(sc, pts, B.toon(c["y"], c["o"]), d=1, name="wing")
    mid = [(1, 9), (15, 13), (8, 7)] if f == 0 else [(15, 9), (1, 13), (8, 7)]
    B.poly(sc, mid, B.flat(c["o"]), d=1, y=-1, name="fold")
    B.box(sc, 7, 10, 3, 1, B.flat(c["r"]), d=1, y=-2, name="txt")


def ebook(sc, f, c):
    B.box(sc, 2, 1, 12, 14, B.toon(c["r"], c["k"]), d=3, rot=(0 if f == 0 else 10), name="cover")
    B.box(sc, 13, 1.5, 1.2, 13, B.flat(c["y"]), d=2.6, rot=(0 if f == 0 else 10), name="pages")
    B.text(sc, "10X", 8, 8, 5.2, B.flat(c["y"]), d=0.5, y=-2)
    B.box(sc, 4, 3.5, 8, 1, B.flat(c["o"]), d=1, y=-2, name="sub")


# ------------------------------------------------------------ slop, ep 3
# Mode 0: 12x16 pixels = 24x16 units
def ape(sc, f, c):
    B.ball(sc, 12, 7.5, 6.6, B.toon(15, 3), sx=1.6, name="head")
    B.ball(sc, 12, 5.5, 4.2, B.toon(16, 15), sx=1.6, sz=0.8, y=-3, name="muzzle")
    B.box(sc, 6, 9, 5, 1.5, B.flat(26), d=1, y=-7, name="lidL")
    B.box(sc, 13, 9, 5, 1.5, B.flat(26), d=1, y=-7, name="lidR")
    B.box(sc, 6, 10.5, 5, 1, B.flat(15), d=1, y=-7.2, name="browL")
    B.box(sc, 13, 10.5, 5, 1, B.flat(15), d=1, y=-7.2, name="browR")
    B.box(sc, 9, 3.5 - f * 0.5, 6, 1.2, B.flat(0), d=1, y=-7.5, name="mouth")
    B.box(sc, 4, 12.5, 16, 3, B.toon(11, 1), d=8, name="cap")
    B.box(sc, 14, 12, 9, 1.5, B.toon(11, 1), d=6, y=-2, name="visor")


def landplot(sc, f, c):
    B.poly(sc, [(2, 8), (22, 8), (16, 1 + f), (8, 1 + f)], B.toon(15, 3), d=4, name="soil")
    B.box(sc, 2, 7, 20, 2.5, B.toon(18, 9), d=6, name="grass")
    B.box(sc, 5, 9.5, 7, 4, B.toon(26, 13), d=3, name="house")
    B.poly(sc, [(4, 13.5), (8.5, 16), (13, 13.5)], B.flat(6), d=3.2, name="roof")
    B.box(sc, 15, 9.5, 1, 5, B.flat(13), d=1, name="pole")
    B.box(sc, 16, 12.5, 6, 2.5, B.flat(24), d=1, name="sign")


def coin(sc, f, c):
    sx = 1.0 if f == 0 else 0.25
    B.cyl(sc, 12, 8, 7.2, 1.5, B.toon(24, 15), axis="Y", name="coin").scale = (sx * 1.5, 1, 1)
    if f == 0:
        B.text(sc, "$", 12, 4.6, 9, B.flat(15), d=0.6, y=-1.2)


def render_items():
    out = []
    jobs = [("items_ep1", 1, [portrait, cat3, hand6], EP1),
            ("items_ep2", 1, [newspaper, plane, ebook], EP2),
            ("items_ep3", 0, [ape, landplot, coin], EP3)]
    for name, mode, kinds, c in jobs:
        for k, fn in enumerate(kinds):
            for f in (0, 1):
                w = 16 if mode == 1 else 12
                sc = B.scene("%s_%d_%d" % (name, k, f), w, 16, 1.0 if mode == 1 else 2.0)
                fn(sc, f, c)
                out.append(B.render(sc, "%s/%d_%d.png" % (name, k, f)))
    return out


# ----------------------------------------------------------- power-ups
def coffee(sc, mode):
    mug = B.toon(26, 20 if mode == 1 else 13)
    if mode == 1:
        B.cyl(sc, 7, 6, 4.5, 8, mug, axis="Z", name="mug")
        B.cyl(sc, 7, 10.1, 3.8, 0.4, B.flat(1), axis="Z", name="coffee")
        B.box(sc, 11, 4, 3, 5, mug, d=2, name="handle")
        for sx in (5, 8.5):
            B.poly(sc, [(sx, 11), (sx + 1.5, 13), (sx, 15), (sx + 1, 15), (sx + 2.5, 13), (sx + 1, 11)],
                   B.flat(8), d=1, y=-5, name="steam")
    else:
        B.cyl(sc, 10, 6, 6, 8, mug, axis="Z", name="mug")
        B.cyl(sc, 10, 10.1, 5, 0.4, B.flat(3), axis="Z", name="coffee")
        B.box(sc, 16, 4, 4, 5, mug, d=2, name="handle")
        for sx in (7, 11):
            B.poly(sc, [(sx, 11), (sx + 2, 13), (sx, 15.5), (sx + 1.5, 15.5), (sx + 3.5, 13), (sx + 1.5, 11)],
                   B.flat(13), d=1, y=-6, name="steam")


def heart(sc, mode):
    if mode == 1:
        m = B.toon(8, 1)
        B.ball(sc, 5.5, 10, 3.6, m, name="lobeL")
        B.ball(sc, 10.5, 10, 3.6, m, name="lobeR")
        B.poly(sc, [(2.1, 9.3), (13.9, 9.3), (8, 1.5)], m, d=4, name="tip")
        B.box(sc, 4, 10.5, 1.5, 1.5, B.flat(26), d=1, y=-4, name="shine")
    else:
        m = B.toon(6, 3)
        B.ball(sc, 8, 10, 4.5, m, sx=1.0, name="lobeL")
        B.ball(sc, 16, 10, 4.5, m, name="lobeR")
        B.poly(sc, [(3.6, 9.2), (20.4, 9.2), (12, 1.5)], m, d=4, name="tip")
        B.box(sc, 6, 10.5, 3, 2, B.flat(26), d=1, y=-5, name="shine")


def render_power(mode):
    out = []
    for i, fn in enumerate((coffee, heart)):
        sc = B.scene("power_m%d_%d" % (mode, i), 16 if mode == 1 else 12, 16, 1.0 if mode == 1 else 2.0)
        fn(sc, mode)
        out.append(B.render(sc, "power_m%d/%d.png" % (mode, i)))
    return out


# --------------------------------------------------------- crypto-bro
def bro(sc, pose, z0=0.0):
    skin = B.toon(16, 16)
    for side, lx in ((-1, 7.5), (1, 13)):
        lift = {"walk1": 1.2, "walk2": -1.2}.get(pose, 0) * side
        lift = max(0, lift)
        B.box(sc, lx, z0 + 1.5 + lift, 3.5, 6, skin, d=3, name="leg")
        B.box(sc, lx - 0.5, z0 + lift, 4.5, 1.8, B.flat(26), d=4, name="shoe")
    B.box(sc, 6.5, z0 + 6, 11, 4, B.toon(11, 1), d=5, name="shorts")
    B.box(sc, 6.5, z0 + 10, 11, 7, B.toon(7, 5), d=5, name="hoodie")
    B.box(sc, 10.5, z0 + 12.5, 3, 2.5, B.flat(24), d=5.4, name="logo")
    B.poly(sc, [(8, z0 + 17), (12, z0 + 13.5), (16, z0 + 17)], B.flat(24), d=1, y=-3, name="chain")
    B.ball(sc, 12, z0 + 20, 3.8, skin, name="head")
    B.box(sc, 8.5, z0 + 22, 7, 2.2, B.flat(0), d=8, y=0.5, name="hair")
    B.box(sc, 8.6, z0 + 19.8, 7, 1.6, B.flat(0), d=1, y=-3.8, name="shades")
    B.box(sc, 10.5, z0 + 17.4, 3, 0.9, B.flat(26), d=1, y=-3.6, name="smile")
    if pose == "float":
        B.box(sc, 4.5, z0 + 14, 2, 8, skin, d=2, name="armUpL")
        B.box(sc, 17.5, z0 + 14, 2, 8, skin, d=2, name="armUpR")
    else:
        B.box(sc, 4.5, z0 + 10, 2, 6, skin, d=2, name="armL")
        B.box(sc, 17.5, z0 + 11, 2, 5, skin, d=2, name="armR")
        B.box(sc, 18, z0 + 15, 3, 4, B.flat(0), d=2, y=-1, name="phone")


def render_bro():
    out = []
    for i, pose in enumerate(("walk1", "walk2")):
        sc = B.scene("bro_walk_%d" % i, 12, 24, 2.0)
        bro(sc, pose)
        out.append(B.render(sc, "bro_walk/%d.png" % i))
    sc = B.scene("bro_float", 12, 32, 2.0)
    bro(sc, "float", z0=0)
    B.ball(sc, 12, 26.5, 5.5, B.toon(20, 11), sx=1.75, name="bubble")
    B.ball(sc, 8.5, 28.5, 1.4, B.flat(26), sx=1.5, y=-9, name="shine")
    B.box(sc, 5, 21, 1, 3, B.flat(26), d=1, name="string")
    B.box(sc, 18, 21, 1, 3, B.flat(26), d=1, name="string")
    out.append(B.render(sc, "bro_float/0.png"))
    return out


def render_all():
    return (render_themis(1) + render_themis(0) + render_robot(1) + render_robot(0) + render_items()
            + render_power(1) + render_power(0) + render_bro())
