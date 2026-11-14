"""MORE SLOP episodes 4-10: slop, decoys, obstacle characters and backgrounds
(run inside Blender: exec this file, then call render_sprites() / render_bgs()).

Same conventions as sprites.py / scenes.py: pixel units, toon materials in
CPC firmware colours, Mode 1 sprites 1:1, Mode 0 sprites with 2:1 pixels
(so an 8-pixel Mode 0 item is 16 units wide). Aseprite snaps the renders to
the episode palettes (tools/aseprite_jobs.py, tools/aseprite/scenes.lua).
"""
import math
import sys
import importlib

sys.path.insert(0, r"\\wsl.localhost\Ubuntu\home\vasilhs\repos\MoreSlopCPC\tools\blender")
import msblend as B  # noqa: E402
importlib.reload(B)
import scenes as SC  # noqa: E402
importlib.reload(SC)

T, F = B.toon, B.flat


def star(sc, x, z, r, mat, y=-6, name="star"):
    pts = []
    for i in range(8):
        a = math.pi / 2 + i * math.pi / 4
        rr = r if i % 2 == 0 else r * 0.35
        pts.append((x + rr * math.cos(a), z + rr * math.sin(a)))
    return B.poly(sc, pts, mat, d=1, y=y, name=name)


# ============================================================ episode 4
# palette: 4 purple (bg), 18 green, 16 pink, 26 white
def fakeface(sc, f):
    skin = T(16, 4)
    B.ball(sc, 8, 8, 5.6, skin, sz=1.15, name="head")
    B.ball(sc, 8, 12.5, 5.2, T(18, 4), sz=0.5, y=0.5, name="hair")
    ey = 9 if f == 0 else 10.2
    B.box(sc, 4.3, 8.5, 3, 2.2, F(26), d=1, y=-5.2, name="eyeL")
    B.box(sc, 8.8, ey, 3, 2.2, F(26), d=1, y=-5.2, name="eyeR")
    B.box(sc, 5.3, 8.8, 1.2, 1.4, F(18), d=1, y=-5.6, name="pupL")
    B.box(sc, 9.8, ey + 0.3, 1.2, 1.4, F(18), d=1, y=-5.6, name="pupR")
    B.box(sc, 5, 4.2, 6, 1.5, F(26), d=1, y=-5.4, name="grin")
    if f:
        B.box(sc, 1, 6.5, 14, 1.4, F(18), d=1, y=-7, name="glitch")
        B.box(sc, 6, 11.5, 9, 1, F(26), d=1, y=-7, name="glitch2")


def lipsync(sc, f):
    pink = T(16, 4)
    B.box(sc, 7.4, 0.5, 1.2, 3.5, F(18), d=1.2, name="pole")
    B.box(sc, 4.5, 0, 7, 1.2, F(18), d=3, name="foot")
    gap = 1.2 + 1.6 * f
    B.ball(sc, 8, 9.5 + gap / 2, 5.6, pink, sx=1.25, sz=0.45, name="upper")
    B.ball(sc, 8, 7.5 - gap / 2, 5.4, pink, sx=1.2, sz=0.5, name="lower")
    B.box(sc, 3.5, 8.5 - gap / 2, 9, gap, F(26) if f else F(4), d=1, y=-1, name="teeth")


def vhs(sc, f):
    rot = 0 if f == 0 else 9
    B.box(sc, 1, 3.5, 14, 9, T(18, 4), d=3, rot=rot, name="tape")
    B.box(sc, 2.5, 8, 11, 3.5, T(26, 16), d=3.4, rot=rot, name="label")
    B.text(sc, "REAL", 8, 8.6 + (0.6 if f else 0), 3.0, F(16), d=0.3, y=-2.2)
    for rx in (4.5, 11.5):
        B.ball(sc, rx, 5.5 + (rx - 8) * math.sin(math.radians(rot)) * 0.1, 1.4, F(26), y=-1.5, name="reel")


def deepfake_themis(sc, f):
    """A deepfake of Themis (16x16): zapping it flips the controls."""
    B.box(sc, 3, 0, 10, 4.5, T(18, 4), d=5, name="shirt")
    hx = 8 + (1.2 if f else 0)
    B.ball(sc, hx, 9, 4.4, T(26, 16), name="head")
    B.ball(sc, hx, 11.6, 4.0, T(16, 4), sz=0.55, y=0.6, name="hair")
    B.poly(sc, [(hx - 1, 12.5), (hx + 1.5, 15.6), (hx + 2.5, 12)], T(16, 4), d=2, y=-2, name="tuft")
    B.box(sc, hx - 3.4, 8.8, 2.8, 1.8, F(4), d=1, y=-4.4, name="glassL")
    B.box(sc, hx + 0.6, 8.8, 2.8, 1.8, F(4), d=1, y=-4.4, name="glassR")
    B.box(sc, hx - 2, 6.4, 4, 0.9, F(4), d=1, y=-4.4, name="grin")
    gy = 7.5 if f == 0 else 10
    B.box(sc, 0.5, gy, 15, 1.2, F(18), d=1, y=-7, name="scanline")
    B.box(sc, 2, gy - 3.2, 6, 0.9, F(26), d=1, y=-7, name="scanline2")


# ============================================================ episode 5
# palette: 0 black (bg), 21 lime, 9 green, 25 pastel yellow
def listicle(sc, f):
    rot = 6 if f == 0 else -6
    B.box(sc, 2, 1, 12, 14, T(25, 9), d=1, rot=rot, name="page")
    B.text(sc, "10", 8, 6.5, 6.5, F(9), d=0.3, y=-1)
    B.box(sc, 3.5, 3, 9, 1, F(21), d=1, y=-1.2, rot=rot, name="line")
    B.box(sc, 3.5, 13, 9, 1, F(21), d=1, y=-1.2, rot=rot, name="line")


def keywordsoup(sc, f):
    B.ball(sc, 8, 6, 6.6, T(21, 9), sz=0.55, name="bowl")
    B.box(sc, 1.5, 6, 13, 1.6, T(9, 0), d=8, name="rim")
    B.text(sc, "SEO", 8, 7.8 + f, 3.6, F(25), d=0.3, y=-4)
    for i, sx in enumerate((4.5, 9.5)):
        sz = 11.5 + ((i + f) % 2)
        B.poly(sc, [(sx, sz), (sx + 1.2, sz + 1.6), (sx, sz + 3.2), (sx + 0.8, sz + 3.2),
                    (sx + 2, sz + 1.6), (sx + 0.8, sz)], F(25), d=1, y=-5, name="steam")


def clickphone(sc, f):
    """A click-farm phone showing a thumbs-up."""
    B.box(sc, 3.5, 0.5, 9, 15, T(9, 0), d=2, name="phone")
    B.box(sc, 4.5, 2.5, 7, 11, F(21), d=2.2, name="screen")
    up = 0.8 * f
    B.box(sc, 5.6, 4 + up, 4.2, 4, F(0), d=1, y=-1.4, name="fist")
    B.box(sc, 7.4, 8 + up, 1.8, 3.6, F(0), d=1, y=-1.4, name="thumb")
    B.box(sc, 9.8, 4.2 + up, 0.9, 3.4, F(0), d=1, y=-1.4, name="cuff")


# ============================================================ episode 6
# Mode 0, 8 px = 16 units wide. pens: 0 k, 23 pcyan, 17 pmagenta, 26 w,
# 14 pblue, 22 pgreen, 3 r, 15 o, 24 y, 16 pk, 18 g, 25 pyellow, 11 sky,
# 13 grey, 6 bright red, 10 cyan
def robophone(sc, f):
    B.box(sc, 2, 1.5, 12, 6.5, T(6, 3), d=6, name="base")
    B.ball(sc, 8, 5, 2.4, F(26), y=-3.4, name="dial")
    B.box(sc, 3.5, 6, 2, 1.4, F(10), d=1, y=-3.4, name="eyeL")
    B.box(sc, 10.5, 6, 2, 1.4, F(10), d=1, y=-3.4, name="eyeR")
    lift = 2.4 * f
    B.box(sc, 2.5, 9.5 + lift, 11, 2.4, T(6, 3), d=3.5, name="handset")
    B.ball(sc, 2.6, 10 + lift, 2.2, T(6, 3), name="ear")
    B.ball(sc, 13.4, 10 + lift, 2.2, T(6, 3), name="mic")
    if f:
        B.box(sc, 0.5, 14.5, 2, 1, F(24), d=1, y=-5, name="ring")
        B.box(sc, 13.5, 14.5, 2, 1, F(24), d=1, y=-5, name="ring")


def helpbubble(sc, f):
    """A chatbot 'typing...' bubble."""
    B.ball(sc, 8, 9.5, 6.6, T(26, 14), sz=0.85, name="bubble")
    B.poly(sc, [(3, 6), (2, 1), (7, 4.5)], T(26, 14), d=2, name="tail")
    for i, dx in enumerate((3.5, 7, 10.5)):
        up = 1.2 if i == (1 + f) % 3 else 0
        B.box(sc, dx, 8.2 + up, 2.4, 2.4, F(0), d=1, y=-6, name="dot")


def holdnote(sc, f):
    dz = 1.0 * f
    B.box(sc, 1, 12.5 + dz, 14, 1.5, F(13), d=2, name="band")
    B.ball(sc, 2, 9 + dz, 2.4, T(13, 0), sx=0.7, name="cupL")
    B.ball(sc, 14, 9 + dz, 2.4, T(13, 0), sx=0.7, name="cupR")
    B.ball(sc, 6.5, 3.5 + dz, 3, T(10, 11), sz=0.75, y=-1, name="notehead")
    B.box(sc, 8.6, 3.5 + dz, 1.6, 9, F(10), d=1, y=-1, name="stem")
    B.poly(sc, [(10, 12.5 + dz), (13, 10 + dz), (12, 8.5 + dz), (10, 10.5 + dz)], F(10), d=1, y=-1, name="flag")


def gary(sc, f):
    """Gary, the last human support agent (do not zap)."""
    B.box(sc, 3, 0, 10, 3.5, T(26, 14), d=5, name="shirt")
    B.box(sc, 7, 0, 2, 3.2, F(6), d=5.4, name="tie")
    B.ball(sc, 8, 8.5, 4.6, T(16, 15), sz=1.05, name="head")
    B.ball(sc, 8, 11.5, 4.4, T(15, 3), sz=0.5, y=0.4, name="hair")
    B.box(sc, 2.6, 7.5, 1.6, 4.5, F(13), d=4, name="earcup")
    B.box(sc, 2.8, 12.6, 10.4, 1, F(13), d=4, name="band")
    B.box(sc, 3.5, 5, 4, 0.8, F(13), d=1, y=-4.5, name="boom")
    if f == 0:
        B.box(sc, 5.6, 9, 1.4, 1.6, F(0), d=1, y=-4.7, name="eyeL")
        B.box(sc, 9.2, 9, 1.4, 1.6, F(0), d=1, y=-4.7, name="eyeR")
    else:
        B.box(sc, 5.4, 9.4, 1.8, 0.6, F(0), d=1, y=-4.7, name="blinkL")
        B.box(sc, 9.0, 9.4, 1.8, 0.6, F(0), d=1, y=-4.7, name="blinkR")
    B.box(sc, 6.4, 6, 3.4, 0.9, F(6), d=1, y=-4.6, name="smile")


# ============================================================ episode 7
# palette: 1 blue (bg), 26 white, 11 sky, 24 yellow
def rocketpost(sc, f):
    B.box(sc, 1, 1, 14, 14, T(26, 11), d=1, name="card")
    r = B.poly(sc, [(6, 4), (11, 9), (12.5, 12.5), (9, 11)], T(24, 11), d=1.4, y=-1, name="rocket")
    B.ball(sc, 10.2, 10.2, 1, F(11), y=-2, name="window")
    if f:
        B.poly(sc, [(6, 4), (3, 2.5), (4.5, 5)], F(24), d=1, y=-1.5, name="flame")
        B.poly(sc, [(6.5, 5.5), (2.5, 6), (5, 3)], F(11), d=1, y=-1.6, name="flame2")
    B.box(sc, 2.5, 2, 5, 0.9, F(11), d=1, y=-1.2, name="agree?")
    return r


def headshot(sc, f):
    B.box(sc, 1.5, 0, 13, 5.5, T(11, 1), d=4, name="suit")
    B.poly(sc, [(5.5, 5.5), (10.5, 5.5), (8, 1)], F(26), d=1, y=-2.2, name="shirt")
    B.poly(sc, [(7.4, 5), (8.6, 5), (9, 1.5), (8, 0.5), (7, 1.5)], F(24), d=1, y=-2.4, name="tie")
    B.ball(sc, 8, 10, 4.2, T(26, 11), sz=1.1, name="head")
    B.ball(sc, 8, 13.2, 4.1, T(24, 11), sz=0.45, y=0.4, name="hair")
    B.box(sc, 5.6, 10.5, 1.4, 1.2, F(1), d=1, y=-4.3, name="eyeL")
    B.box(sc, 9, 10.5, 1.4, 1.2, F(1), d=1, y=-4.3, name="eyeR")
    B.box(sc, 5.6, 7.3, 4.8, 1.2, F(26), d=1, y=-4.4, name="teeth")
    B.box(sc, 5.6, 7.0, 4.8, 0.4, F(1), d=1, y=-4.5, name="lip")
    if f:
        star(sc, 11.5, 8.5, 2.2, F(24), y=-6)


def broetry(sc, f):
    off = f * 1.2
    B.box(sc, 3.5, 1.5, 9, 13, T(26, 11), d=1, name="scroll")
    B.cyl(sc, 8, 14.5, 1.2, 10.5, T(24, 11), axis="X", name="rollT")
    B.cyl(sc, 8, 1.5, 1.2, 10.5, T(24, 11), axis="X", name="rollB")
    for i, w in enumerate((3, 6, 2, 5, 3, 7, 2)):
        z = 12.2 - i * 1.6 - off
        if 2.6 < z < 13:
            B.box(sc, 8 - w / 2, z, w, 0.8, F(11), d=1, y=-1, name="line")


def guru(sc, pose, z0=0.0, pal=None):
    """A thought leader (Mode 1, 24 units wide). pal: skin, hair, jacket, shirt, pants, accent"""
    p = pal or dict(skin=(26, 11), hair=(24, 11), jacket=(26, 11), shirt=(11, 1), pants=(11, 1), acc=(24, 24))
    skin = T(*p["skin"])
    for side, lx in ((-1, 7.5), (1, 13)):
        lift = max(0, {"walk1": 1.2, "walk2": -1.2}.get(pose, 0) * side)
        B.box(sc, lx, z0 + 1.5 + lift, 3.5, 6.5, T(*p["pants"]), d=3, name="leg")
        B.box(sc, lx - 0.5, z0 + lift, 4.5, 1.8, T(*p["acc"]), d=4, name="shoe")
    B.box(sc, 6.5, z0 + 7.5, 11, 9.5, T(*p["jacket"]), d=5, name="blazer")
    B.poly(sc, [(10, z0 + 17), (14, z0 + 17), (12, z0 + 11)], T(*p["shirt"]), d=1, y=-2.8, name="shirt")
    B.box(sc, 11.4, z0 + 8, 1.2, 9, T(*p["acc"]), d=1, y=-3, name="lanyard")
    B.box(sc, 10.5, z0 + 7.5, 3, 2.2, T(*p["acc"]), d=1, y=-3.2, name="badge")
    B.ball(sc, 12, z0 + 20, 3.8, skin, name="head")
    B.ball(sc, 12, z0 + 22.6, 3.7, T(*p["hair"]), sz=0.5, y=0.4, name="hair")
    B.box(sc, 9.8, z0 + 20.2, 1.3, 1.2, F(0), d=1, y=-3.8, name="eyeL")
    B.box(sc, 12.9, z0 + 20.2, 1.3, 1.2, F(0), d=1, y=-3.8, name="eyeR")
    B.box(sc, 10.5, z0 + 17.6, 3, 0.9, T(*p["acc"]), d=1, y=-3.6, name="smile")
    B.box(sc, 8.2, z0 + 18, 4, 0.6, T(*p["acc"]), d=1, y=-3.9, name="headsetmic")
    if pose == "float":
        B.box(sc, 4.5, z0 + 13, 2, 8, T(*p["jacket"]), d=2, name="armUpL")
        B.box(sc, 17.5, z0 + 13, 2, 8, T(*p["jacket"]), d=2, name="armUpR")
    else:
        B.box(sc, 4.5, z0 + 9, 2, 7, T(*p["jacket"]), d=2, name="armL")
        B.box(sc, 17.5, z0 + 10, 2, 6, T(*p["jacket"]), d=2, name="armR")
        B.box(sc, 18, z0 + 15, 3.4, 2.4, T(*p["acc"]), d=1, y=-1.5, name="clicker")


def render_guru(name, pal, balloon, balloon_txt, txt_col):
    out = []
    for i, pose in enumerate(("walk1", "walk2")):
        sc = B.scene("%s_walk_%d" % (name, i), 24, 24, 1.0)
        guru(sc, pose, pal=pal)
        out.append(B.render(sc, "%s_walk/%d.png" % (name, i)))
    sc = B.scene("%s_float" % name, 24, 32, 1.0)
    guru(sc, "float", z0=0, pal=pal)
    B.ball(sc, 12, 27, 5.2, T(*balloon), sx=1.7, name="balloon")
    B.text(sc, balloon_txt, 12, 25.4, 3.6, F(txt_col), d=0.3, y=-5.6)
    B.box(sc, 5, 21, 1, 3, F(26), d=1, name="string")
    B.box(sc, 18, 21, 1, 3, F(26), d=1, name="string")
    out.append(B.render(sc, "%s_float/0.png" % name))
    return out


# ============================================================ episode 8
# Mode 0. pens: 0 k, 23 pcyan, 17 pmag, 26 w, 12 olive, 25 pyellow, 3 r,
# 15 o, 24 y, 16 pk, 18 g, 9 dg, 11 sky, 13 grey, 6 bred, 4 magenta
def gluepizza(sc, f):
    B.poly(sc, [(1, 14), (15, 14), (8, 1.5)], T(24, 15), d=2, name="slice")
    B.box(sc, 1, 12.5, 14, 2.6, T(15, 3), d=3, name="crust")
    for (px, pz) in ((5.5, 10), (10, 9.5), (7.8, 6)):
        B.ball(sc, px, pz, 1.5, T(6, 3), y=-1.5, name="pepperoni")
    L = 3 + 2.5 * f
    for gx in (4.5, 11):
        B.box(sc, gx, 12.5 - L, 1.2, L, F(26), d=1, y=-2, name="glue")
        B.ball(sc, gx + 0.6, 12.5 - L, 0.9, F(26), y=-2, name="drop")


def rocksalad(sc, f):
    B.ball(sc, 8, 5.5, 7, T(26, 13), sz=0.55, name="bowl")
    B.box(sc, 1, 5.5, 14, 1.6, T(23, 13), d=8, name="rim")
    for (lx, lz) in ((4, 8.5), (11.5, 8.2), (8, 9.5)):
        B.ball(sc, lx, lz, 2.4, T(18, 9), sx=1.3, sz=0.7, y=-0.5, name="leaf")
    for i, (rx, rz) in enumerate(((6, 9.5), (10, 10.5))):
        B.ball(sc, rx, rz + (f if i == 0 else -f) * 0.8 + 1, 2.2, T(13, 0), y=-2.5, name="rock")


def screwspaghetti(sc, f):
    B.ball(sc, 8, 4, 7.4, T(26, 13), sz=0.25, name="plate")
    for i in range(6):
        s = B.box(sc, 3 + i * 1.6, 4.5 + (i % 2), 5, 0.9, F(24), d=2, y=-1, name="strand")
        s.rotation_euler = (0, math.radians(30 * ((i * 7 + f * 3) % 5) - 60), 0)
    for (sx, sz) in ((5, 7), (10.5, 8)):
        B.box(sc, sx, sz, 1.2, 3.2, F(13), d=1, y=-3, name="screw")
        B.box(sc, sx - 0.6, sz + 3, 2.4, 0.9, F(13), d=1, y=-3, name="screwhead")
    B.box(sc, 12.5 - f, 6, 1, 9, F(13), d=1, y=-4, name="fork")


def chef(sc, pose, z0=0.0):
    """A chef-bot (Mode 0, 24 units wide)."""
    body = T(13, 0)
    for side, lx in ((-1, 8), (1, 13)):
        lift = max(0, {"walk1": 1.2, "walk2": -1.2}.get(pose, 0) * side)
        B.box(sc, lx, z0 + 1.5 + lift, 3, 5.5, body, d=3, name="leg")
        B.box(sc, lx - 0.5, z0 + lift, 4, 1.8, F(0), d=4, name="foot")
    B.box(sc, 6.5, z0 + 6.5, 11, 8.5, T(26, 13), d=5, name="apron")
    B.box(sc, 6.5, z0 + 14, 11, 2, T(6, 3), d=5.4, name="scarf")
    B.box(sc, 7.5, z0 + 16, 9, 6, body, d=5, name="head")
    B.box(sc, 8.5, z0 + 17, 7, 4, F(0), d=5.4, name="screen")
    B.box(sc, 9.3, z0 + 18.6, 1.8, 1.4, F(18), d=1, y=-3, name="eyeL")
    B.box(sc, 12.9, z0 + 18.6, 1.8, 1.4, F(18), d=1, y=-3, name="eyeR")
    B.box(sc, 7, z0 + 22, 10, 2, T(26, 13), d=6, name="hatband")
    B.ball(sc, 12, z0 + 25.5, 4.4, T(26, 13), sx=1.1, sz=0.9, name="toque")
    if pose == "float":
        B.box(sc, 4.5, z0 + 11, 2, 8, body, d=2, name="armUpL")
        B.box(sc, 17.5, z0 + 11, 2, 8, body, d=2, name="armUpR")
    else:
        B.box(sc, 4.5, z0 + 8, 2, 6, body, d=2, name="armL")
        B.box(sc, 17.5, z0 + 9, 2, 5, body, d=2, name="armR")
        B.cyl(sc, 21, z0 + 13, 2.6, 1, T(13, 0), axis="Z", name="pan")
        B.box(sc, 18, z0 + 12.6, 2, 0.8, F(0), d=1, name="handle")


def render_chef():
    out = []
    for i, pose in enumerate(("walk1", "walk2")):
        sc = B.scene("chef_walk_%d" % i, 12, 24, 2.0)
        chef(sc, pose, z0=-4)
        out.append(B.render(sc, "chef_walk/%d.png" % i))
    sc = B.scene("chef_float", 12, 32, 2.0)
    chef(sc, "float", z0=-2)
    B.ball(sc, 12, 28.5, 4.2, T(15, 3), sx=2.0, name="balloon")
    B.box(sc, 5, 22, 1, 4, F(26), d=1, name="string")
    B.box(sc, 18, 22, 1, 4, F(26), d=1, name="string")
    out.append(B.render(sc, "chef_float/0.png"))
    return out


# ============================================================ episode 9
# Mode 0. pens: 0 k, 20 bcyan, 8 bmag, 26 w, 4 mag, 2 bblue, 3 r, 15 o,
# 24 y, 16 pk, 18 g, 21 lime, 11 sky, 13 grey, 6 bred, 7 purple
def vinyl(sc, f):
    d = B.cyl(sc, 8, 8.5, 6.6, 1, T(7, 4), axis="Y", name="disc")
    B.cyl(sc, 8, 8.5, 2.4, 1.2, T(8, 4), axis="Y", y=-0.5, name="label")
    B.ball(sc, 8, 8.5, 0.6, F(26), y=-1.5, name="hole")
    B.box(sc, 3, 11.5, 3, 0.7, F(20), d=1, y=-1.2, name="shine")
    if f:
        for (dx, L) in ((4.5, 4), (10, 6)):
            B.box(sc, dx, 2.5 - L + 2, 1.6, L, T(7, 4), d=1, name="drip")
            B.ball(sc, dx + 0.8, 2.5 - L + 2, 1, T(7, 4), name="drop")
    return d


def automic(sc, f):
    B.box(sc, 7, 0.5, 2.4, 8, T(4, 7), d=2.4, name="handle")
    B.ball(sc, 8.2, 11, 3.6, T(13, 0), sz=1.1, name="head")
    for i in range(3):
        B.box(sc, 5.4, 9.8 + i * 1.3, 5.6, 0.4, F(0), d=1, y=-3.7, name="grille")
    r = 1 + f
    for side in (-1, 1):
        for k in range(1 + f):
            B.box(sc, 8.2 + side * (5 + k * 1.6) - 0.4, 10 - r, 0.8, 2 + 2 * r, F(20), d=1, y=-2, name="wave")


def cassette(sc, f):
    B.box(sc, 1, 3.5, 14, 9.5, T(15, 3), d=2, name="body")
    B.box(sc, 2.5, 8.5, 11, 3.5, F(26), d=2.2, name="label")
    B.box(sc, 3, 9.6, 10, 0.6, F(8), d=2.4, name="labelline")
    for rx in (5, 11):
        B.ball(sc, rx, 6, 1.9, F(7), y=-1.5, name="reel")
        a = math.radians(45 * f)
        s = B.box(sc, rx - 0.3, 5, 0.6, 2, F(26), d=1, y=-2.6, name="spoke")
        s.rotation_euler = (0, a, 0)


# ============================================================ episode 10
# palette: 0 black (bg), 20 cyan, 6 red, 26 white
def gpu(sc, f):
    B.box(sc, 0.5, 4, 15, 8, T(20, 0), d=2, name="pcb")
    B.box(sc, 0.5, 2.5, 4, 1.5, F(26), d=1, name="pins")
    for fx in (4.5, 11):
        B.cyl(sc, fx, 8, 3, 1, T(26, 20), axis="Y", y=-1.4, name="fan")
        B.ball(sc, fx, 8, 1.2, F(6), y=-2.2, name="hot")
    if f:
        for fx in (3, 8, 12.5):
            B.poly(sc, [(fx - 1.5, 12), (fx, 15.5), (fx + 1.5, 12)], F(6), d=1, y=-1, name="flame")
    B.box(sc, 7.4, 4 - 1.5 * (1 + f), 1.2, 1.5 * (1 + f), F(6), d=1, y=-1.2, name="drip")


def agiclock(sc, f):
    B.cyl(sc, 8, 8, 7, 1.5, T(20, 0), axis="Y", name="frame")
    B.cyl(sc, 8, 8, 5.8, 1.7, T(26, 20), axis="Y", y=-0.2, name="face")
    for a in range(0, 360, 90):
        x = 8 + 4.6 * math.cos(math.radians(a))
        z = 8 + 4.6 * math.sin(math.radians(a))
        B.box(sc, x - 0.4, z - 0.4, 0.8, 0.8, F(0), d=1, y=-1.5, name="tick")
    for (length, ang) in ((4.6, 80 - 30 * f), (3, 200 + 40 * f)):
        h = B.box(sc, 7.6, 8, 0.8, length, F(6), d=1, y=-1.8, name="hand")
        h.rotation_euler = (0, math.radians(90 - ang), 0)
    B.ball(sc, 8, 8, 0.8, F(0), y=-2.2, name="pin")


def doomphone(sc, f):
    B.box(sc, 3.5, 0.5, 9, 15, T(20, 0), d=2, name="phone")
    B.box(sc, 4.5, 2.5, 7, 11, F(26), d=2.2, name="screen")
    for i in range(4):
        z = 11.5 - i * 3 + (1.5 if f else 0)
        if 2.8 < z < 13:
            B.box(sc, 5.2, z, 5.6, 0.9, F(0), d=2.4, name="post")
            B.ball(sc, 10, z - 0.9, 0.6, F(6), y=-1.4, name="like")


# ======================================================== render jobs
# name, mode, item functions (kinds 0-2)
ITEMS = [
    ("items_ep4", 1, [fakeface, lipsync, vhs]),
    ("items_ep5", 1, [listicle, keywordsoup, clickphone]),
    ("items_ep6", 0, [robophone, helpbubble, holdnote]),
    ("items_ep7", 1, [rocketpost, headshot, broetry]),
    ("items_ep8", 0, [gluepizza, rocksalad, screwspaghetti]),
    ("items_ep9", 0, [vinyl, automic, cassette]),
    ("items_ep10", 1, [gpu, agiclock, doomphone]),
]
DECOYS = [("decoy_ep4", 1, deepfake_themis), ("decoy_ep6", 0, gary)]
EVANG = dict(skin=(26, 20), hair=(20, 0), jacket=(20, 0), shirt=(26, 20), pants=(6, 0), acc=(6, 6))


def scene_for(name, mode):
    return B.scene(name, 16 if mode == 1 else 8, 16, 1.0 if mode == 1 else 2.0)


def render_sprites():
    out = []
    for name, mode, kinds in ITEMS:
        for k, fn in enumerate(kinds):
            for f in (0, 1):
                sc = scene_for("%s_%d_%d" % (name, k, f), mode)
                fn(sc, f)
                out.append(B.render(sc, "%s/%d_%d.png" % (name, k, f)))
    for name, mode, fn in DECOYS:
        for f in (0, 1):
            sc = scene_for("%s_%d" % (name, f), mode)
            fn(sc, f)
            out.append(B.render(sc, "%s/%d.png" % (name, f)))
    out += render_guru("guru", None, (24, 11), "EGO", 1)
    out += render_guru("evang", EVANG, (6, 0), "AGI", 26)
    out += render_chef()
    return out


# ======================================================== backgrounds
lmat, persp, lineart, sky, group = SC.lmat, SC.persp, SC.lineart, SC.sky, SC.group


def bg4():
    """The deepfake studio: green screen, lights, cameras (line art)."""
    sc = B.scene("bg4", 320, 150)
    lineart(sc)
    wall = lmat(4, 4)
    gr = lmat(4, 18)
    pk = lmat(4, 16)
    wh = lmat(4, 26)
    persp(sc, (0, -62, 10), (0, 0, 9), lens=19)
    B.box(sc, -130, -40, 260, 120, wall, d=2, y=32, name="wall")
    B.box(sc, -34, -6, 68, 38, gr, d=1, y=30, name="greenscreen")
    for i in range(-3, 4):
        for j in range(3):
            x, z = i * 9, 2 + j * 10
            B.box(sc, x - 1.5, z - 0.25, 3, 0.5, wh, d=0.5, y=29, name="mark")
            B.box(sc, x - 0.25, z - 1.5, 0.5, 3, wh, d=0.5, y=29, name="mark")
    B.box(sc, -12, 34, 24, 8, pk, d=2, y=28, name="onair")
    B.text(sc, "ON AIR", 0, 36.2, 3.8, lmat(4, 26), d=0.3, y=26.8)
    B.box(sc, -72, 30, 18, 7, pk, d=2, y=28, name="sign2")
    B.text(sc, "TAKE 999", -63, 32, 2.6, lmat(4, 18), d=0.3, y=26.8)
    # lights on stands
    for sx in (-48, 48):
        B.cyl(sc, sx, 8, 0.6, 30, wh, y=18, axis="Z", name="stand")
        lamp = B.box(sc, sx - 5, 22, 10, 7, pk, d=7, y=18, name="lamp")
        lamp.rotation_euler = (0, math.radians(-25 if sx < 0 else 25), 0)
        for k in (-1, 1):
            leg = B.box(sc, sx - 0.4, -7, 0.8, 9, wh, d=0.8, y=18, name="leg")
            leg.rotation_euler = (0, math.radians(25 * k), 0)
    # cameras
    for sx, rz in ((-30, 20), (30, -20)):
        g = B.box(sc, sx - 6, 6, 12, 7, wh, d=8, y=4, name="camera")
        g.rotation_euler = (0, 0, math.radians(rz))
        B.cyl(sc, sx - 6 * (1 if sx > 0 else -1) * 0, 9.5, 2.4, 6, gr, y=-1, axis="Y", name="lens")
        B.cyl(sc, sx, -2, 0.6, 8, wh, y=4, axis="Z", name="tripod")
        for k in (-1, 1):
            leg = B.box(sc, sx - 0.4, -9, 0.8, 9, wh, d=0.8, y=4, name="tleg")
            leg.rotation_euler = (0, math.radians(28 * k), 0)
    # a head on a stand being scanned
    B.ball(sc, 0, 14, 5, wh, y=14, name="dummy")
    B.cyl(sc, 0, 4, 1, 10, pk, y=14, axis="Z", name="neck")
    for i in range(4):
        B.box(sc, -8, 9 + i * 3, 16, 0.4, gr, d=0.4, y=8, name="scan")
    # cables
    for z, x0 in ((-8, -70), (-9, -40)):
        B.cyl(sc, 0, z, 0.8, 150, gr, y=6 + (z + 8) * 6, axis="X", name="cable")
    B.render(sc, "scenes/bg4.png")


def bg5():
    """The SEO content farm: barn, silo, page crops, a keyword scarecrow."""
    sc = B.scene("bg5", 320, 150)
    lineart(sc)
    gnd = lmat(0, 9)
    li = lmat(0, 21)
    yl = lmat(0, 25)
    dk = lmat(0, 9)
    persp(sc, (0, -70, 18), (0, 0, 10), lens=21)
    # barn and silo
    B.box(sc, -62, 0, 30, 20, li, d=16, y=30, name="barn")
    B.poly(sc, [(-64, 20), (-47, 32), (-30, 20)], li, d=17, y=30, name="roof")
    B.box(sc, -52, 0, 10, 12, yl, d=1, y=21.5, name="door")
    B.text(sc, "SEO", -47, 22, 4.5, lmat(0, 25), d=0.3, y=21.6)
    B.cyl(sc, -24, 15, 5, 30, dk, y=32, axis="Z", name="silo")
    B.ball(sc, -24, 30, 5, dk, y=32, name="dome")
    B.text(sc, "#1", -24, 18, 4, lmat(0, 25), d=0.3, y=26.6)
    # windmill made of a server
    B.box(sc, 46, 0, 8, 26, li, d=6, y=34, name="tower")
    for a in (0, 90, 180, 270):
        bl = B.box(sc, 50 - 1, 26, 2, 14, yl, d=0.6, y=30.5, name="blade")
        bl.rotation_euler = (0, math.radians(a + 20), 0)
        bl.location = (50, 30.5, 26)
    for i in range(5):
        B.box(sc, 47, 3 + i * 4.5, 6, 1, yl, d=0.4, y=30.8, name="led")
    # fields of pages growing in rows
    for r in range(5):
        y = 2 + r * 6
        for c in range(-8, 9):
            x = c * 7 + (r % 2) * 3.5
            if -36 < x < 40 and r < 3 or -22 < x < 30:
                B.box(sc, x, 0, 0.4, 3, dk, d=0.4, y=y - 22, name="stalk")
                B.box(sc, x - 1.6, 3, 3.2, 4, yl, d=0.3, y=y - 22, name="page")
    # fence
    for i in range(-11, 12):
        B.box(sc, i * 7, 0, 0.8, 4, li, d=0.8, y=-30, name="post")
    for z in (1.4, 3.2):
        B.box(sc, -80, z, 160, 0.5, li, d=0.5, y=-30, name="rail")
    # the scarecrow
    B.box(sc, 64, 0, 1, 18, dk, d=1, y=6, name="pole")
    B.box(sc, 58, 13, 13, 1, dk, d=1, y=6, name="arms")
    B.box(sc, 60.5, 7, 8, 7, li, d=2, y=5.5, name="shirt")
    B.text(sc, "KEY", 64.5, 9.6, 2.2, lmat(0, 25), d=0.2, y=4.3)
    B.ball(sc, 64.5, 17.5, 2.6, yl, y=6, name="head")
    B.poly(sc, [(60, 19.4), (64.5, 23), (69, 19.4)], li, d=2, y=6, name="hat")
    B.box(sc, -90, -10, 180, 10, gnd, d=120, y=40, name="ground")
    B.render(sc, "scenes/bg5.png")


def bg6():
    """The chatbot helpline: a pastel call centre staffed by robots (Mode 0)."""
    sc = B.scene("bg6", 160, 150, 2.0)
    persp(sc, (0, -70, 14), (0, 0, 11), lens=30)
    B.box(sc, -120, -40, 240, 120, T(14, 2), d=2, y=40, name="wall")
    B.box(sc, -120, -40, 240, 40, T(22, 13), d=200, y=60, name="floor")
    # the sign
    B.box(sc, -30, 32, 60, 10, T(17, 16), d=1, y=38, name="banner")
    B.text(sc, "PLEASE HOLD", 0, 34.2, 5.4, F(26), d=0.3, y=37)
    # clock and queue display
    B.cyl(sc, 44, 33, 6, 1, T(26, 13), axis="Y", y=38, name="clock")
    B.box(sc, 43.6, 32.5, 0.8, 5, F(0), d=1, y=36.5, name="hand")
    B.box(sc, 43.6, 32.5, 4, 0.8, F(0), d=1, y=36.5, name="hand")
    B.box(sc, -56, 28, 20, 12, T(0, 0), d=1, y=38, name="board")
    B.text(sc, "WAIT", -46, 34, 3.6, F(24), d=0.3, y=37)
    B.text(sc, "3H", -46, 29, 4.2, F(6), d=0.3, y=37)
    # rows of desks with robot agents
    for r, (yy, xs) in enumerate(((22, (-45, -15, 15, 45)), (2, (-56, -20, 20, 56)))):
        for x in xs:
            B.box(sc, x - 10, 0, 20, 7, T(25, 12), d=8, y=yy, name="desk")
            B.box(sc, x - 4, 7, 8, 6, T(13, 0), d=1.5, y=yy + 2, name="monitor")
            B.box(sc, x - 3, 8, 6, 4, F(10), d=1.7, y=yy + 2, name="screen")
            B.box(sc, x - 4, 9, 8, 7, T(13, 0), d=5, y=yy + 6, name="botbody")
            B.box(sc, x - 3.5, 16, 7, 6, T(26, 13), d=5, y=yy + 6, name="bothead")
            B.box(sc, x - 2.5, 18, 1.5, 1.5, F(10), d=1, y=yy + 3.4, name="eye")
            B.box(sc, x + 1, 18, 1.5, 1.5, F(10), d=1, y=yy + 3.4, name="eye")
            B.box(sc, x - 4.2, 21.5, 8.4, 1, F(0), d=1, y=yy + 3.4, name="headset")
            B.box(sc, x - 4.5, 16, 1, 4, F(0), d=1, y=yy + 3.4, name="cup")
    # a sad plant
    B.cyl(sc, 70, 4, 4, 8, T(15, 3), axis="Z", y=-4, name="pot")
    for k in range(3):
        lf = B.ball(sc, 68 + k * 2, 10 + k, 2.4, T(18, 9), sz=0.5, y=-4, name="leaf")
        lf.rotation_euler = (0, math.radians(40 - 40 * k), 0)
    B.render(sc, "scenes/bg6.png")


def bg7():
    """The thought leader summit: stage, big screen, spotlights (line art)."""
    sc = B.scene("bg7", 320, 150)
    lineart(sc)
    wall = lmat(1, 1)
    wh = lmat(1, 26)
    sk = lmat(1, 11)
    yl = lmat(1, 24)
    persp(sc, (0, -66, 10), (0, 0, 9), lens=24)
    B.box(sc, -90, -40, 180, 110, wall, d=2, y=34, name="wall")
    # the screen with a chart that only goes up
    B.box(sc, -26, 8, 52, 26, wh, d=1, y=32, name="screen")
    B.text(sc, "SYNERGY", 0, 26, 5.2, lmat(1, 24), d=0.3, y=30.8)
    pts = [(-20, 11), (-12, 13), (-4, 12), (4, 16), (12, 19), (19, 24)]
    for (x0, z0), (x1, z1) in zip(pts, pts[1:]):
        seg = B.box(sc, x0, z0, math.hypot(x1 - x0, z1 - z0), 0.6, sk, d=0.5, y=30.8, name="chart")
        seg.rotation_euler = (0, -math.atan2(z1 - z0, x1 - x0), 0)
    B.poly(sc, [(18, 26.5), (21.5, 22.5), (17, 22)], yl, d=0.5, y=30.8, name="arrow")
    # side banners
    for sx, t in ((-50, "10X"), (50, "AGREE?")):
        B.box(sc, sx - 8, 4, 16, 28, sk, d=1, y=30, name="banner")
        B.text(sc, t, sx, 18, 3.6 if len(t) > 3 else 5, lmat(1, 26), d=0.3, y=28.8)
    # the stage and the lectern
    B.box(sc, -60, -8, 120, 6, wh, d=24, y=18, name="stage")
    B.box(sc, -5, -2, 10, 12, sk, d=6, y=12, name="lectern")
    B.box(sc, -6, 9.5, 12, 1.5, wh, d=8, y=11, name="top")
    B.cyl(sc, 2, 13, 0.3, 6, yl, axis="Z", y=10, name="mic")
    # spotlights
    for sx in (-40, -14, 14, 40):
        B.cyl(sc, sx, 40, 3, 5, sk, axis="Z", y=20, name="spot")
        beam = B.box(sc, sx - 0.3, 6, 0.6, 34, yl, d=0.3, y=20, name="beam")
        beam.rotation_euler = (0, math.radians(sx * 0.45), 0)
    # the audience
    for r in range(2):
        for i in range(-9, 10):
            x = i * 8 + r * 4
            B.ball(sc, x, -10 + r * 3, 3, sk, y=-12 + r * 8, name="head")
            B.box(sc, x - 3.5, -18 + r * 3, 7, 6, wh, d=4, y=-12 + r * 8, name="shoulders")
    B.render(sc, "scenes/bg7.png")


def bg8():
    """The AI kitchen: tiles, stove, pots, a fridge and a big bottle of glue (Mode 0)."""
    sc = B.scene("bg8", 160, 150, 2.0)
    persp(sc, (0, -70, 20), (0, 0, 15), lens=29)
    tileA, tileB = T(23, 14), T(26, 13)
    for i in range(-10, 11):
        for j in range(0, 9):
            B.box(sc, i * 8, j * 6 - 4, 8, 6, tileA if (i + j) % 2 else tileB, d=1, y=40, name="tile")
    B.box(sc, -120, -40, 240, 36, T(12, 0), d=200, y=60, name="floor")
    # counter with stove
    B.box(sc, -80, -4, 160, 14, T(12, 0), d=14, y=28, name="counter")
    B.box(sc, -80, 10, 160, 2, T(25, 12), d=15, y=28, name="worktop")
    for i in range(-5, 5):
        B.box(sc, i * 16 + 1.5, -2, 13, 10, T(25, 12), d=1, y=20.6, name="cupboard")
        B.box(sc, i * 16 + 6, 6, 4, 0.8, F(13), d=1, y=20.2, name="knob")
    for x in (-22, -6):
        B.cyl(sc, x, 14, 5, 7, T(13, 0), axis="Z", y=24, name="pot")
        B.box(sc, x - 6, 20, 12, 1.2, T(13, 0), d=12, y=24, name="lid")
        for k in range(2):
            st = B.ball(sc, x - 2 + 4 * k, 26 + k * 3, 2.4, F(26), sz=1.4, y=24, name="steam")
    # the glue bottle
    B.box(sc, 10, 12, 8, 14, T(24, 15), d=6, y=24, name="glue")
    B.box(sc, 12.5, 26, 3, 3, T(6, 3), d=3, y=24, name="cap")
    B.text(sc, "GLUE", 14, 17, 2.6, F(6), d=0.3, y=20.8)
    # rocks on a cutting board
    B.box(sc, 22, 12, 18, 2, T(15, 3), d=10, y=24, name="board")
    for k in range(3):
        B.ball(sc, 26 + k * 5, 15.5, 2.2 + (k % 2) * 0.6, T(13, 0), y=24, name="rock")
    # fridge
    B.box(sc, 44, -4, 20, 46, T(26, 13), d=14, y=26, name="fridge")
    B.box(sc, 44, 22, 20, 0.8, F(13), d=14.4, y=26, name="door")
    B.box(sc, 46, 26, 1.2, 8, F(13), d=15, y=26, name="handle")
    B.text(sc, "AI", 54, 30, 4.5, F(6), d=0.3, y=18.6)
    # hanging pans
    B.box(sc, -70, 40, 50, 1, F(13), d=1, y=36, name="rail")
    for x in (-64, -52, -38, -26):
        B.box(sc, x - 0.3, 32, 0.6, 8, F(13), d=0.6, y=35, name="hook")
        B.cyl(sc, x, 28, 4, 1, T(0, 0), axis="Y", y=35, name="pan")
    # a robot chef's sad recipe card
    B.box(sc, -64, 14, 14, 16, T(26, 14), d=1, y=27, name="card")
    for k in range(4):
        B.box(sc, -62, 26 - k * 3, 10, 0.8, F(16), d=1, y=26.4, name="line")
    B.render(sc, "scenes/bg8.png")


def bg9():
    """The slop-fi festival: night stage, speaker stacks, lasers, a crowd (Mode 0)."""
    sc = B.scene("bg9", 160, 150, 2.0)
    persp(sc, (0, -70, 12), (0, 0, 12), lens=30)
    sky(sc, B.lin((0.0, 0.0, 0.15)), B.lin((0.25, 0.0, 0.40)), B.lin((0.50, 0.0, 0.50)))
    # truss and stage
    B.box(sc, -60, -6, 120, 8, T(13, 0), d=26, y=30, name="stage")
    B.box(sc, -58, 44, 116, 2, T(13, 0), d=2, y=26, name="truss")
    for x in (-58, 56):
        B.box(sc, x, 2, 2, 42, T(13, 0), d=2, y=26, name="tower")
    # DJ booth
    B.box(sc, -16, 2, 32, 12, T(7, 4), d=8, y=24, name="booth")
    B.text(sc, "SLOP-FI", 0, 5.5, 4.6, F(20), d=0.3, y=19.8)
    for x in (-10, 8):
        B.cyl(sc, x, 14.5, 4, 0.8, T(13, 0), axis="Z", y=24, name="deck")
    # the DJ: the SlopBot's cousin
    B.box(sc, -5, 14, 10, 10, T(26, 13), d=6, y=27, name="dj")
    B.box(sc, -3.5, 16, 7, 6, F(0), d=6.4, y=27, name="djscreen")
    B.box(sc, -2.5, 18.5, 1.5, 1.5, F(21), d=1, y=23.6, name="eye")
    B.box(sc, 1, 18.5, 1.5, 1.5, F(21), d=1, y=23.6, name="eye")
    B.box(sc, -6, 23, 12, 1.4, F(8), d=8, y=27, name="headphones")
    # speaker stacks
    for x in (-50, 36):
        for k in range(3):
            B.box(sc, x, 2 + k * 11, 14, 11, T(0, 0), d=10, y=26, name="speaker")
            B.cyl(sc, x + 7, 7.5 + k * 11, 4, 1, T(13, 0), axis="Y", y=20.6, name="cone")
            B.ball(sc, x + 7, 7.5 + k * 11, 1.4, F(8), y=19.8, name="dust")
    # lasers
    for i, (a, c) in enumerate(((-35, 20), (-15, 8), (15, 21), (35, 20))):
        b = B.box(sc, -0.4, 44, 0.8, 70, F(c), d=0.8, y=28, name="laser")
        b.rotation_euler = (0, math.radians(180 + a), 0)
        b.location = (0, 28, 44)
    # stars
    for (x, z) in ((-70, 60), (-40, 66), (-10, 62), (30, 68), (62, 58), (75, 66)):
        B.ball(sc, x, z, 0.8, F(26), y=60, name="star")
    # the crowd, hands up
    for r in range(2):
        for i in range(-10, 11):
            x = i * 7 + r * 3.5
            B.ball(sc, x, -6 + r * 3, 3, T(7, 4), y=-10 + r * 8, name="head")
            if (i + r) % 3 == 0:
                B.box(sc, x + 2, -4 + r * 3, 1.2, 7, T(7, 4), d=1.2, y=-10 + r * 8, name="hand")
    B.render(sc, "scenes/bg9.png")


def bg10():
    """The data centre: server racks receding to the SlopBot's core (line art)."""
    sc = B.scene("bg10", 320, 150)
    lineart(sc)
    blk = lmat(0, 0)
    cy = lmat(0, 20)
    rd = lmat(0, 6)
    wh = lmat(0, 26)
    persp(sc, (0, -8, 2), (0, 100, -2), lens=16)
    for i in range(9):
        y = 6 + i * 14
        for side in (-1, 1):
            x = -26 if side < 0 else 14
            B.box(sc, x, -15, 12, 30, cy, d=12, y=y, name="rack")
            for k in range(6):
                B.box(sc, x + (12.2 if side < 0 else -0.6), -11 + k * 4.4, 0.4, 2.6,
                      wh if (i + k) % 3 else rd, d=8, y=y, name="unit")
                B.box(sc, x + (12.4 if side < 0 else -0.8), -10 + k * 4.4, 0.3, 0.6,
                      rd if (i * 7 + k) % 4 == 0 else cy, d=1, y=y - 3, name="led")
    # cable trays overhead
    for x in (-8, 8):
        B.box(sc, x - 2, 14, 4, 1, rd, d=140, y=70, name="tray")
    # floor grid
    for i in range(12):
        B.box(sc, -14, -15.2, 28, 0.2, cy, d=0.6, y=4 + i * 11, name="tile")
    # the core at the end: the SlopBot's red eye
    B.cyl(sc, 0, 0, 9, 2, rd, axis="Y", y=132, name="core")
    B.cyl(sc, 0, 0, 5, 2.4, wh, axis="Y", y=131, name="iris")
    B.cyl(sc, 0, 0, 2, 2.8, rd, axis="Y", y=130, name="pupil")
    B.text(sc, "SLOPBOT", 0, 11, 3.4, lmat(0, 26), d=0.3, y=128)
    B.render(sc, "scenes/bg10.png")


def render_bgs():
    out = []
    for fn in (bg4, bg5, bg6, bg7, bg8, bg9, bg10):
        fn()
        out.append(fn.__name__)
    return out


def save():
    names = []
    for name, mode, kinds in ITEMS:
        names += ["%s_%d_%d" % (name, k, f) for k in range(3) for f in (0, 1)]
    for name, mode, fn in DECOYS:
        names += ["%s_%d" % (name, f) for f in (0, 1)]
    for n in ("guru", "evang", "chef"):
        names += ["%s_walk_0" % n, "%s_walk_1" % n, "%s_float" % n]
    B.save_blend("sprites_ep4_10", only=names)
    return B.save_blend("scenes_ep4_10", only=["bg%d" % n for n in range(4, 11)])
