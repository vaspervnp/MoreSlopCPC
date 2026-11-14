"""MORE SLOP full-screen pictures (run inside Blender; exec, then call).

  bg1   the Hallucination Factory - Freestyle line art on dark blue
  bg2   the Clickbait Express     - amber line art, one-point corridor
  bg3   the Crypto Graveyard      - toon-shaded night scene (Mode 0)
  menu  title picture: scene + logo rendered apart (logo -> rainbow pens)
  loader the loading screen
Renders go to art/renders/scenes/; Aseprite then dithers them to the CPC
palettes (tools/aseprite/scenes.lua).
"""
import math
import sys
import importlib

sys.path.insert(0, r"\\wsl.localhost\Ubuntu\home\vasilhs\repos\MoreSlopCPC\tools\blender")
import msblend as B  # noqa: E402
importlib.reload(B)
import sprites as SP  # noqa: E402
importlib.reload(SP)

import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402


def persp(sc, loc, look, lens=35):
    cam = sc.camera
    cam.data.type = "PERSP"
    cam.data.lens = lens
    cam.location = loc
    d = Vector(look) - Vector(loc)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def lineart(sc, thickness=1.0):
    sc.render.use_freestyle = True
    sc.render.line_thickness_mode = "ABSOLUTE"
    sc.render.line_thickness = thickness
    vl = sc.view_layers[0]
    vl.use_freestyle = True
    fs = vl.freestyle_settings
    ls = fs.linesets[0] if len(fs.linesets) else fs.linesets.new("MS_lines")
    ls.select_by_visibility = True
    ls.select_by_edge_types = True
    ls.select_silhouette = True
    ls.select_border = True
    ls.select_crease = True
    ls.select_contour = True
    st = ls.linestyle
    st.thickness = thickness
    st.chaining = "PLAIN"
    for m in list(st.color_modifiers):
        st.color_modifiers.remove(m)
    mod = st.color_modifiers.new("by_material", "MATERIAL")
    mod.material_attribute = "LINE"
    mod.blend = "MIX"
    mod.influence = 1.0
    return st


def lmat(face_fw, line_fw, name=None):
    """Flat face colour + Freestyle line colour (firmware numbers)."""
    m = B.toon(face_fw, face_fw, name=name or "MS_line_%d_%d" % (face_fw, line_fw))
    m.line_color = B.lin(B.fw_rgb(line_fw))
    return m


def group(sc, fn, *args, loc=(0, 0, 0), scale=1.0, rot_z=0.0, **kw):
    """Build fn(sc, ...) and parent everything it made to an empty."""
    before = set(sc.objects)
    fn(sc, *args, **kw)
    new = [o for o in sc.objects if o not in before]
    e = bpy.data.objects.new("grp", None)
    sc.collection.objects.link(e)
    for o in new:
        if o.parent is None:
            o.parent = e
    e.location = loc
    e.scale = (scale, scale, scale)
    e.rotation_euler = (0, 0, math.radians(rot_z))
    return e


def gear(sc, x, y, z, r, teeth, mat, depth=2.0, rot=0.0):
    B.cyl(sc, x, z, r, depth, mat, y=y, axis="Y", seg=32, name="gear")
    B.cyl(sc, x, z, r * 0.3, depth + 0.6, mat, y=y, axis="Y", seg=16, name="hub")
    for i in range(teeth):
        a = rot + 2 * math.pi * i / teeth
        tx, tz = x + (r + 0.6) * math.cos(a), z + (r + 0.6) * math.sin(a)
        t = B.box(sc, tx - 0.8, tz - 0.8, 1.6, 1.6, mat, d=depth, y=y, name="tooth")
        t.rotation_euler = (0, -a, 0)


# --------------------------------------------------------------- episode 1
def bg1():
    sc = B.scene("bg1", 320, 150)
    lineart(sc)
    wall = lmat(1, 1)               # invisible: dark blue on dark blue
    cy = lmat(1, 20)                # cyan lines
    mg = lmat(1, 8)                 # magenta lines
    wh = lmat(1, 26)
    persp(sc, (0, -60, 8), (0, 0, 4), lens=24)
    B.box(sc, -80, -40, 160, 100, wall, d=2, y=30, name="wall")
    # wall panels
    for i in range(-5, 6):
        B.box(sc, i * 12 - 5, -10, 10, 40, cy, d=1, y=28.5, name="panel")
    gear(sc, -38, 26, 22, 9, 12, mg, rot=0.2)
    gear(sc, -22, 25, 10, 5, 8, cy, rot=0.5)
    gear(sc, 42, 26, 20, 7, 10, mg, rot=0.1)
    # the big screen: a smiley that is slightly wrong
    B.box(sc, -12, 12, 26, 18, wh, d=2, y=26, name="screen")
    B.ball(sc, -5, 22, 1.6, mg, y=24.5, name="eye")
    B.ball(sc, 6, 23, 2.4, mg, y=24.5, name="eye2")
    B.box(sc, -6, 15.5, 13, 1.2, mg, d=1, y=24.5, rot=-6, name="mouth")
    B.text(sc, "GENERATING...", 1, 9, 2.6, lmat(1, 20), d=0.3, y=24.5)
    # pipes
    for z in (34, 37):
        B.cyl(sc, 0, z, 1.2, 160, cy, y=22, axis="X", name="pipe")
    for x in (-58, 58):
        B.cyl(sc, x, 10, 1.5, 50, cy, y=20, axis="Z", name="vpipe")
    # robot arms
    for sx in (-1, 1):
        B.box(sc, sx * 30 - 2, 0, 4, 18, wh, d=4, y=14, name="armbase")
        B.box(sc, sx * 30 - 2, 16, 16 * sx if sx > 0 else 16, 3, cy, d=3, y=14, name="arm")
    # conveyor belt with rollers
    B.box(sc, -70, -6, 140, 4, cy, d=8, y=6, name="belt")
    for i in range(-8, 9):
        B.cyl(sc, i * 8, -6, 1.6, 8.5, mg, y=6, axis="Y", seg=12, name="roller")
    for i, x in enumerate(range(-60, 70, 22)):
        B.box(sc, x, -2, 5, 5, wh if i % 2 else mg, d=4, y=6, rot=20 * i, name="slop")
    B.render(sc, "scenes/bg1.png")


# --------------------------------------------------------------- episode 2
def bg2():
    sc = B.scene("bg2", 320, 150)
    lineart(sc)
    blk = lmat(0, 0)
    o = lmat(0, 15)                 # orange lines
    r = lmat(0, 3)                  # dark red lines
    y = lmat(0, 24)
    persp(sc, (0, -40, 0), (0, 100, 0), lens=18)
    # corridor frames receding
    for i in range(10):
        d = i * 14
        for (x, z, w, h) in ((-26, -16, 52, 1.5), (-26, 15, 52, 1.5), (-26, -16, 1.5, 32), (24.5, -16, 1.5, 32)):
            B.box(sc, x, z, w, h, o if i % 2 == 0 else r, d=1.5, y=d, name="frame")
    # book shelves on the walls
    for side in (-1, 1):
        for i in range(8):
            yy = 4 + i * 14
            for s in range(3):
                z = -10 + s * 8
                B.box(sc, side * 22 - (4 if side > 0 else 0), z, 4, 0.6, r, d=10, y=yy, name="shelf")
                for b in range(4):
                    B.box(sc, side * 22 - (3.5 if side > 0 else -0.5) + 0, z + 0.6, 3, 4 + (b % 2),
                          y if (b + i) % 3 == 0 else o, d=1.2, y=yy - 4 + b * 2.4, name="book")
    # floating "CLICK" screens
    for i, (x, z, t) in enumerate(((-10, 6, "CLICK"), (9, 2, "LIKE"), (-3, -2, "SHARE"))):
        B.box(sc, x - 5, z - 2, 10, 5, o, d=0.5, y=30 + i * 22, name="sign")
        B.text(sc, t, x, z - 1, 2.4, lmat(0, 24), d=0.2, y=29.6 + i * 22)
    # conveyor of books along the floor
    B.box(sc, -10, -15, 20, 1, r, d=140, y=60, name="conveyor")
    for i in range(12):
        B.box(sc, -4 + (i % 2) * 3, -14, 5, 3, y if i % 2 else o, d=2, y=4 + i * 11, name="ebook")
    B.render(sc, "scenes/bg2.png")


# --------------------------------------------------------------- episode 3
def sky(sc, top, mid, low):
    """Backdrop plane with a vertical gradient (linear colours)."""
    m = bpy.data.materials.new("MS_sky")
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    e = ramp.color_ramp.elements
    e[0].position = 0.0
    e[0].color = low
    e[1].position = 1.0
    e[1].color = top
    mid_e = e.new(0.45)
    mid_e.color = mid
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    p = B.box(sc, -300, -100, 800, 400, m, d=1, y=150, name="sky")
    return p


def tomb(sc, x, y, z, w, h, label, mat, txt):
    B.box(sc, x - w / 2, z, w, h - w / 2, mat, d=3, y=y, name="tomb")
    B.cyl(sc, x, z + h - w / 2, w / 2, 3, mat, y=y, axis="Y", seg=20, name="tombtop")
    if label:
        B.text(sc, label, x, z + h * 0.45, w * 0.32, txt, d=0.3, y=y - 1.7)


def bg3():
    sc = B.scene("bg3", 160, 150, 2.0)
    persp(sc, (0, -70, 14), (0, 0, 12), lens=30)
    sky(sc, B.lin((0.0, 0.0, 0.25)), B.lin((0.30, 0.0, 0.45)), B.lin((0.55, 0.0, 0.35)))
    B.ball(sc, 34, 62, 11, B.toon(26, 13), y=140, name="moon")
    B.ball(sc, 30, 64, 2.5, B.flat(13), y=128, name="crater")
    B.ball(sc, 38, 58, 1.8, B.flat(13), y=128, name="crater")
    # hills
    for i, (x, r, c) in enumerate(((-60, 40, 1), (10, 34, 5), (70, 44, 1))):
        B.ball(sc, x, -22, r, B.toon(c, 0), sz=0.6, y=90 - i * 6, name="hill")
    ground = B.toon(1, 0)
    B.box(sc, -150, -40, 300, 40, ground, d=200, y=50, name="ground")
    stone = B.toon(13, 1)
    txt = B.flat(0)
    for i, (x, y, w, h, lab) in enumerate(((-44, 30, 10, 16, "APE"), (-22, 18, 8, 13, "RUG"),
                                           (24, 22, 9, 15, "NFT"), (46, 34, 11, 18, "HODL"),
                                           (0, 40, 8, 12, "WEB3"), (-60, 50, 9, 14, ""), (64, 52, 9, 14, ""))):
        tomb(sc, x, y, 0, w, h, lab, stone, txt)
    # the neon sign, half dead
    B.box(sc, -9, 20, 30, 9, B.toon(0, 0), d=1, y=58, name="signboard")
    B.text(sc, "TO THE MOON", 6, 22.5, 3.6, B.flat(8), d=0.4, y=56.5)
    B.box(sc, -8, 0, 1, 20, B.flat(13), d=1, y=58, name="post")
    B.box(sc, 19, 0, 1, 20, B.flat(13), d=1, y=58, name="post")
    # crashed rocket
    r = B.cyl(sc, -32, 10, 3, 18, B.toon(26, 13), y=60, axis="Z", name="rocket")
    r.rotation_euler = (math.radians(-10), math.radians(35), 0)
    B.text(sc, "$", -32, 6, 6, B.flat(24), d=0.4, y=56)
    # dead trees
    for x in (-70, 72):
        B.box(sc, x, 0, 2, 26, B.flat(0), d=2, y=40, name="trunk")
        for k in range(3):
            b = B.box(sc, x - 6 + k * 4, 14 + k * 4, 10, 1.2, B.flat(0), d=1.5, y=40, name="branch")
            b.rotation_euler = (0, math.radians(30 - 30 * k), 0)
    sun = [o for o in sc.objects if o.type == "LIGHT"][0]
    sun.data.color = (0.8, 0.8, 1.0)
    B.render(sc, "scenes/bg3.png")


# ----------------------------------------------------------- menu / loader
def logo(name, w, h, aspect, size, base):
    """MORE SLOP in chunky 3D letters with slime drips. Rendered white-ish;
    build_assets maps its brightness onto the three rainbow pens."""
    sc = B.scene(name, w, h, aspect)      # ortho: 1 unit = 1 visual pixel
    m = B.toon(26, 13, split=0.5)
    W = w * aspect
    t = B.text(sc, "MORE SLOP", W / 2, base, size, m, d=4)
    t.data.bevel_depth = 0.8
    t.data.space_character = 1.05
    t.rotation_euler = (math.radians(80), math.radians(0), math.radians(-12))
    for i, x in enumerate((0.16, 0.27, 0.43, 0.58, 0.66, 0.81, 0.90)):
        L = (8, 13, 6, 15, 9, 11, 5)[i]
        B.box(sc, W * x, base - L + 2, 2.4, L, m, d=2, y=-6, name="drip")
        B.ball(sc, W * x + 1.2, base - L + 2, 2.0, m, y=-6, name="drop")
    return sc


def menu():
    sc = logo("menu_logo", 160, 60, 2.0, 50, 22)
    B.render(sc, "scenes/menu_logo.png")
    # the scene under the logo: Themis zaps the SlopBot and its heap (320x60 units)
    sc = B.scene("menu_scene", 160, 60, 2.0)
    sky(sc, B.lin((0.0, 0.0, 0.15)), B.lin((0.15, 0.0, 0.35)), B.lin((0.45, 0.0, 0.45)))
    group(sc, SP.themis, SP.THEMIS_M0, "zap", loc=(30, 0, 2), scale=2.2)
    group(sc, SP.robot, SP.ROBOT_M0, True, loc=(200, 0, 14), scale=2.2)
    heap = [(SP.landplot, 0, 150, 0, 1.4), (SP.ape, 0, 196, 0, 1.4), (SP.coin, 0, 238, 1, 1.2),
            (SP.ape, 1, 262, 2, 1.3), (SP.coin, 1, 290, 0, 1.2)]
    for fn, f, x, z, s in heap:
        group(sc, fn, f, SP.EP3, loc=(x, -10, z), scale=s)
    pts = [(86, 50), (118, 40), (110, 38), (150, 30), (122, 34), (130, 36), (84, 47)]
    B.poly(sc, pts, B.flat(24), d=1, y=-20, name="bolt")
    B.render(sc, "scenes/menu_scene.png")


def loader():
    sc = logo("loader_logo", 160, 50, 2.0, 46, 18)
    B.render(sc, "scenes/loader_logo.png")
    sc = B.scene("loader_scene", 160, 150, 2.0)    # 320x150 units
    sky(sc, B.lin((0.0, 0.0, 0.10)), B.lin((0.20, 0.0, 0.40)), B.lin((0.85, 0.15, 0.25)))
    group(sc, SP.robot, SP.ROBOT_M0, True, loc=(96, 40, 62), scale=4.0)
    heap = [(SP.hand6, 0, 10, 0, 2.6, SP.EP1), (SP.cat3, 1, 52, 10, 2.4, SP.EP1),
            (SP.ape, 0, 150, 2, 2.6, SP.EP3), (SP.coin, 0, 204, 14, 2.0, SP.EP3),
            (SP.landplot, 1, 236, 0, 2.4, SP.EP3), (SP.portrait, 1, 270, 18, 2.2, SP.EP1),
            (SP.ebook, 0, 96, 22, 2.0, SP.EP2), (SP.newspaper, 1, 286, 0, 2.0, SP.EP2)]
    for fn, f, x, z, s, c in heap:
        group(sc, fn, f, c, loc=(x, -20, z), scale=s)
    group(sc, SP.themis, SP.THEMIS_M0, "zap", loc=(124, -40, 0), scale=2.6)
    pts = [(170, 68), (190, 84), (184, 86), (206, 104), (192, 90), (198, 88), (172, 70)]
    B.poly(sc, pts, B.flat(24), d=1, y=-60, name="bolt")
    B.render(sc, "scenes/loader_scene.png")


def render_all():
    bg1()
    bg2()
    bg3()
    menu()
    loader()
    return B.save_blend("scenes")
