"""Blender helpers for MORE SLOP art (run inside Blender via the MCP).

Models are built from primitives in "pixel units": 1 Blender unit = 1 sprite
pixel, seen by an orthographic camera looking along +Y. Materials are toon
shaders whose two colours (lit / shadow) are CPC palette colours, so the
render already speaks the CPC's language; Aseprite then snaps and outlines.
"""
import math
import os

import bpy

REPO = r"\\wsl.localhost\Ubuntu\home\vasilhs\repos\MoreSlopCPC"
RENDERS = os.path.join(REPO, "art", "renders")

LV = (0, 0x80, 0xFF)


def fw_rgb(fw):
    g, rest = divmod(fw, 9)
    r, b = divmod(rest, 3)
    return (LV[r] / 255.0, LV[g] / 255.0, LV[b] / 255.0)


def lin(c):
    def f(v):
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return (f(c[0]), f(c[1]), f(c[2]), 1.0)


# ------------------------------------------------------------------ scene
def scene(name, w, h, aspect_x=1.0):
    """Fresh scene MS_<name> with camera, light and render settings."""
    sname = "MS_" + name
    old = bpy.data.scenes.get(sname)
    if old:
        for ob in list(old.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.scenes.remove(old)
    sc = bpy.data.scenes.new(sname)
    r = sc.render
    r.engine = "BLENDER_EEVEE"
    r.resolution_x = w
    r.resolution_y = h
    r.resolution_percentage = 100
    r.pixel_aspect_x = aspect_x
    r.pixel_aspect_y = 1.0
    r.film_transparent = True
    r.filter_size = 0.0
    r.image_settings.file_format = "PNG"
    r.image_settings.color_mode = "RGBA"
    try:
        sc.eevee.taa_render_samples = 1
    except Exception:
        pass
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0
    sc.view_settings.gamma = 1.0
    world = bpy.data.worlds.get("MS_world") or bpy.data.worlds.new("MS_world")
    world.color = (0, 0, 0)
    sc.world = world
    # camera
    cd = bpy.data.cameras.new(sname + "_cam")
    cd.type = "ORTHO"
    cam = bpy.data.objects.new(sname + "_cam", cd)
    sc.collection.objects.link(cam)
    cam.location = (w * aspect_x / 2.0, -100.0, h / 2.0)
    cam.rotation_euler = (math.radians(90), 0, 0)
    cd.ortho_scale = max(w * aspect_x, h)
    cd.clip_end = 400
    sc.camera = cam
    # key light from the upper left, in front
    ld = bpy.data.lights.new(sname + "_sun", "SUN")
    ld.energy = 6.0
    sun = bpy.data.objects.new(sname + "_sun", ld)
    sc.collection.objects.link(sun)
    from mathutils import Vector
    # light travels right, away from the camera and down: lit from front-top-left
    sun.rotation_euler = Vector((0.45, 1.0, -0.75)).to_track_quat("-Z", "Y").to_euler()
    return sc


def render(sc, rel_path):
    path = os.path.join(RENDERS, rel_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True, scene=sc.name)
    return path


# -------------------------------------------------------------- materials
_mats = {}


def toon(lit, shadow=None, name=None, split=0.45):
    """Two-tone toon material from firmware colours (shadow defaults to lit)."""
    if shadow is None:
        shadow = lit
    key = name or "MS_toon_%d_%d_%.2f" % (lit, shadow, split)
    m = bpy.data.materials.get(key)
    if m:
        return m
    m = bpy.data.materials.new(key)
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    if lit == shadow:
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = lin(fw_rgb(lit))
        em.inputs["Strength"].default_value = 1.0
        nt.links.new(em.outputs[0], out.inputs["Surface"])
        return m
    dif = nt.nodes.new("ShaderNodeBsdfDiffuse")
    s2r = nt.nodes.new("ShaderNodeShaderToRGB")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    e = ramp.color_ramp.elements
    e[0].position = 0.0
    e[0].color = lin(fw_rgb(shadow))
    e[1].position = split
    e[1].color = lin(fw_rgb(lit))
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(dif.outputs[0], s2r.inputs[0])
    nt.links.new(s2r.outputs["Color"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m


def flat(fw):
    return toon(fw, fw)


# ------------------------------------------------------------- primitives
def _link(sc, ob, mat, parent=None):
    sc.collection.objects.link(ob)
    if mat is not None:
        ob.data.materials.append(mat)
    if parent is not None:
        ob.parent = parent
    return ob


def _mesh(name, verts, faces):
    import bmesh
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    me.update()
    return me


def box(sc, x, z, w, h, mat, d=4.0, y=0.0, name="box", rot=0.0, parent=None):
    """Axis box: left x, bottom z, width w, height h (pixels), depth d."""
    v = []
    for dz in (0, h):
        for dy in (-d / 2, d / 2):
            for dx in (0, w):
                v.append((dx - w / 2, dy, dz - h / 2))
    f = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    ob = bpy.data.objects.new(name, _mesh(name, v, f))
    ob.location = (x + w / 2, y, z + h / 2)
    ob.rotation_euler = (0, math.radians(rot), 0)
    return _link(sc, ob, mat, parent)


def ball(sc, x, z, r, mat, y=0.0, sx=1.0, sz=1.0, sy=1.0, name="ball", seg=24, parent=None):
    """UV sphere centred at (x, z)."""
    v, f = [], []
    rings = seg // 2
    for i in range(rings + 1):
        t = math.pi * i / rings
        for j in range(seg):
            p = 2 * math.pi * j / seg
            v.append((r * sx * math.sin(t) * math.cos(p), r * sy * math.sin(t) * math.sin(p),
                      r * sz * math.cos(t)))
    for i in range(rings):
        for j in range(seg):
            a = i * seg + j
            b = i * seg + (j + 1) % seg
            f.append((a, b, b + seg, a + seg))
    ob = bpy.data.objects.new(name, _mesh(name, v, f))
    ob.location = (x, y, z)
    return _link(sc, ob, mat, parent)


def cyl(sc, x, z, r, h, mat, y=0.0, axis="Y", name="cyl", seg=24, rot=0.0, parent=None):
    """Cylinder centred at (x, z), along `axis` (Y = facing the camera)."""
    v, f = [], []
    for k in (-h / 2, h / 2):
        for j in range(seg):
            p = 2 * math.pi * j / seg
            a, b = r * math.cos(p), r * math.sin(p)
            if axis == "Y":
                v.append((a, k, b))
            elif axis == "Z":
                v.append((a, b, k))
            else:
                v.append((k, a, b))
    for j in range(seg):
        n = (j + 1) % seg
        f.append((j, n, n + seg, j + seg))
    f.append(tuple(range(seg))[::-1])
    f.append(tuple(range(seg, 2 * seg)))
    ob = bpy.data.objects.new(name, _mesh(name, v, f))
    ob.location = (x, y, z)
    ob.rotation_euler = (0, math.radians(rot), 0)
    return _link(sc, ob, mat, parent)


def poly(sc, pts, mat, d=2.0, y=0.0, name="poly", parent=None):
    """Extruded 2D polygon (pts in x, z)."""
    n = len(pts)
    v = [(x, -d / 2 + y, z) for x, z in pts] + [(x, d / 2 + y, z) for x, z in pts]
    f = [tuple(range(n))[::-1], tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        f.append((i, j, j + n, i + n))
    ob = bpy.data.objects.new(name, _mesh(name, v, f))
    return _link(sc, ob, mat, parent)


def text(sc, s, x, z, size, mat, d=1.0, y=0.0, name="text", font=None, align="CENTER"):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = s
    cu.size = size
    cu.extrude = d
    cu.align_x = align
    if font:
        cu.font = font
    ob = bpy.data.objects.new(name, cu)
    ob.location = (x, y, z)
    ob.rotation_euler = (math.radians(90), 0, 0)
    sc.collection.objects.link(ob)
    ob.data.materials.append(mat)
    return ob


def save_blend(name="moreslop"):
    """Write only the MS_ scenes (and what they use) to art/blender/<name>.blend,
    leaving whatever else is open in Blender alone."""
    p = os.path.join(REPO, "art", "blender", name + ".blend")
    scenes = {s for s in bpy.data.scenes if s.name.startswith("MS_")}
    bpy.data.libraries.write(p, scenes, fake_user=True)
    return p
