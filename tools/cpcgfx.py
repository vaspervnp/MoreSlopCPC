"""CPC graphics helpers: palette, Mode 0/1 encoders, screen layout, LZ packer.

Everything that turns pictures into bytes for the Z80 goes through here, so
the encoders are written once and checked once (see selftest()).
"""
import os

from PIL import Image

# --- the 27 CPC colours ---------------------------------------------------
# firmware number = 9*G + 3*R + B, with each gun in {0, 1, 2}
FW_TO_HW = [0x14, 0x04, 0x15, 0x1C, 0x18, 0x1D, 0x0C, 0x05, 0x0D,
            0x16, 0x06, 0x17, 0x1E, 0x00, 0x1F, 0x0E, 0x07, 0x0F,
            0x12, 0x02, 0x13, 0x1A, 0x19, 0x1B, 0x0A, 0x03, 0x0B]

FW_NAMES = ["black", "blue", "bright blue", "red", "magenta", "mauve",
            "bright red", "purple", "bright magenta", "green", "cyan",
            "sky blue", "yellow", "white", "pastel blue", "orange", "pink",
            "pastel magenta", "bright green", "sea green", "bright cyan",
            "lime", "pastel green", "pastel cyan", "bright yellow",
            "pastel yellow", "bright white"]


def fw_rgb(fw):
    g, rest = divmod(fw, 9)
    r, b = divmod(rest, 3)
    lv = (0, 0x80, 0xFF)
    return (lv[r], lv[g], lv[b])


def ga_colour(fw):
    """Byte to OUT to the gate array to set the selected pen to `fw`."""
    return 0x40 | FW_TO_HW[fw]


def hexrgb(fw):
    return "#%02X%02X%02X" % fw_rgb(fw)


# --- palettes (firmware numbers, by pen) -----------------------------------
PAL = {
    # Episode 1 - Mode 1: dark blue background, cyan, magenta, white
    "ep1": [1, 20, 8, 26],
    # Episode 2 - Mode 1 amber phosphor
    "ep2": [0, 15, 3, 24],
    # Episode 3 - Mode 0, sixteen loud colours (pens 0-3 match the Mode 1 roles)
    "ep3": [0, 20, 8, 26, 1, 5, 3, 15, 24, 16, 18, 9, 11, 13, 6, 7],
    # Mode 1 episodes keep the roles: pen 0 background, 1 main, 2 second, 3 highlight
    "ep4": [4, 18, 16, 26],     # deepfake studio: purple, green screen, pink, white
    "ep5": [0, 21, 9, 25],      # SEO farm: terminal lime and green
    "ep7": [1, 26, 11, 24],     # thought leaders: corporate blue, white, sky, gold
    "ep10": [0, 20, 6, 26],     # singularity: server cyan and red alert
    # Mode 0 episodes keep pens 0,3,6-10,12-14 (Themis, the robot, effects) and
    # repaint 1, 2, 4, 5, 11, 15
    "ep6": [0, 23, 17, 26, 14, 22, 3, 15, 24, 16, 18, 25, 11, 13, 6, 10],   # pastel helpline
    "ep8": [0, 23, 17, 26, 12, 25, 3, 15, 24, 16, 18, 9, 11, 13, 6, 4],     # kitchen
    "ep9": [0, 20, 8, 26, 4, 2, 3, 15, 24, 16, 18, 21, 11, 13, 6, 7],       # neon festival
    # HUD (Mode 1) - one per episode
    "hud1": [0, 24, 8, 26],
    "hud2": [0, 24, 15, 26],
    "hud3": [0, 24, 18, 26],
    "hud4": [0, 24, 16, 26],
    "hud5": [0, 24, 21, 26],
    "hud6": [0, 24, 23, 26],
    "hud7": [0, 24, 11, 26],
    "hud8": [0, 24, 15, 26],
    "hud9": [0, 24, 8, 26],
    "hud10": [0, 24, 6, 26],
    # shelf strip at the bottom of Mode 1 episodes (pen 0 = playfield pen 0)
    "shelf1": [1, 3, 15, 24],
    "shelf2": [0, 3, 15, 24],
    "shelf4": [4, 3, 15, 24],
    "shelf5": [0, 3, 15, 24],
    "shelf7": [1, 3, 15, 24],
    "shelf10": [0, 3, 15, 24],
    # menu (Mode 0); pens 1-3 cycle through the rainbow for the logo
    "menu": [0, 6, 15, 24, 1, 2, 5, 8, 7, 18, 20, 11, 16, 13, 26, 3],
    # loading screen (Mode 0), set by the BASIC loader with INK
    "loader": [0, 1, 2, 5, 8, 7, 6, 15, 24, 18, 20, 11, 16, 13, 26, 3],
}


def pal_rgb(name):
    return [fw_rgb(f) for f in PAL[name]]


# --- byte encoders ----------------------------------------------------------
def m0_byte(p0, p1):
    return (((p0 & 1) << 7) | ((p1 & 1) << 6) |
            (((p0 >> 2) & 1) << 5) | (((p1 >> 2) & 1) << 4) |
            (((p0 >> 1) & 1) << 3) | (((p1 >> 1) & 1) << 2) |
            (((p0 >> 3) & 1) << 1) | ((p1 >> 3) & 1))


def m1_byte(px):
    b = 0
    for i, p in enumerate(px):
        b |= ((p & 1) << (7 - i)) | (((p >> 1) & 1) << (3 - i))
    return b


def encode_row(pens, mode):
    """pens: list of pen numbers for one line. Returns bytes."""
    if mode == 0:
        assert len(pens) % 2 == 0
        return bytes(m0_byte(pens[i], pens[i + 1]) for i in range(0, len(pens), 2))
    assert len(pens) % 4 == 0
    return bytes(m1_byte(pens[i:i + 4]) for i in range(0, len(pens), 4))


def mask_row(opaque, mode):
    """opaque: list of bools per pixel. Mask byte keeps (1) the screen bits
    of transparent pixels and clears (0) the bits of opaque ones."""
    out = []
    if mode == 0:
        for i in range(0, len(opaque), 2):
            m = 0xFF
            if opaque[i]:
                m &= ~0xAA
            if opaque[i + 1]:
                m &= ~0x55
            out.append(m & 0xFF)
    else:
        for i in range(0, len(opaque), 4):
            m = 0xFF
            for k in range(4):
                if opaque[i + k]:
                    m &= ~((0x80 >> k) | (0x08 >> k))
            out.append(m & 0xFF)
    return bytes(out)


def line_offset(y):
    return (y >> 3) * 80 + (y & 7) * 0x800


# --- picture -> pens ----------------------------------------------------------
def nearest(rgb, pal):
    best, bd = 0, 1 << 30
    for i, c in enumerate(pal):
        d = (rgb[0] - c[0]) ** 2 + (rgb[1] - c[1]) ** 2 + (rgb[2] - c[2]) ** 2
        if d < bd:
            best, bd = i, d
    return best


def image_pens(img, pal, alpha=True):
    """Map an RGBA image to rows of pens; returns (pens, opaque)."""
    img = img.convert("RGBA")
    w, h = img.size
    px = img.load()
    pens, opq = [], []
    cache = {}
    for y in range(h):
        pr, orow = [], []
        for x in range(w):
            r, g, b, a = px[x, y]
            o = (a >= 128) or not alpha
            k = (r, g, b)
            if k not in cache:
                cache[k] = nearest(k, pal)
            pr.append(cache[k] if o else 0)
            orow.append(o)
        pens.append(pr)
        opq.append(orow)
    return pens, opq


def sprite_bytes(img, pal, mode, trim=True):
    """Masked sprite: db w_bytes, h, dx_bytes, dy, then per line (mask, data)
    pairs. Fully transparent byte columns and lines are trimmed away; dx/dy
    say where the trimmed block sits inside the frame."""
    pens, opq = image_pens(img, pal)
    w, h = img.size
    ppb = 2 if mode == 0 else 4
    wb = w // ppb
    cols = [any(opq[y][x] for y in range(h) for x in range(c * ppb, c * ppb + ppb)) for c in range(wb)]
    rows = [any(r) for r in opq]
    if trim and any(rows):
        c0 = cols.index(True)
        c1 = wb - cols[::-1].index(True)
        r0 = rows.index(True)
        r1 = h - rows[::-1].index(True)
    else:
        c0, c1, r0, r1 = 0, wb, 0, h
    out = bytearray([c1 - c0, r1 - r0, c0, r0])
    for y in range(r0, r1):
        d = encode_row(pens[y], mode)
        m = mask_row(opq[y], mode)
        for i in range(c0, c1):
            out += bytes([m[i], d[i]])
    return bytes(out)


def opaque_bytes(img, pal, mode):
    pens, _ = image_pens(img, pal, alpha=False)
    return b"".join(encode_row(r, mode) for r in pens)


def screen_from_bands(bands):
    """bands: list of (y0, y1, mode, pens_rows) where pens_rows cover y0..y1-1
    and are 160 (mode 0) or 320 (mode 1) pens wide. Returns 16K screen RAM."""
    scr = bytearray(0x4000)
    for y0, y1, mode, rows in bands:
        for y in range(y0, y1):
            row = encode_row(rows[y - y0], mode)
            assert len(row) == 80, (len(row), mode)
            o = line_offset(y)
            scr[o:o + 80] = row
    return bytes(scr)


# --- LZ packer (format decoded by src/lz.asm) ---------------------------------
# token t < 0x80 : t+1 literal bytes follow
# token t >= 0x80: copy (t & 0x7F) + 3 bytes from dst - offset, offset = next word
# a match with offset 0 ends the stream
def lz_pack(data):
    data = bytes(data)
    n = len(data)
    out = bytearray()
    lit = bytearray()
    head = {}
    i = 0

    def flush():
        nonlocal lit
        while lit:
            chunk = lit[:128]
            out.append(len(chunk) - 1)
            out.extend(chunk)
            lit = lit[128:]

    while i < n:
        best_len, best_off = 0, 0
        if i + 3 <= n:
            key = data[i:i + 3]
            cands = head.get(key, [])
            for p in reversed(cands[-64:]):
                off = i - p
                if off > 0xFFFF:
                    continue
                l = 0
                while i + l < n and l < 130 and data[p + l] == data[i + l]:
                    l += 1
                if l > best_len:
                    best_len, best_off = l, off
                    if l == 130:
                        break
        if best_len >= 3:
            flush()
            out.append(0x80 | (best_len - 3))
            out += bytes([best_off & 0xFF, best_off >> 8])
            for k in range(best_len):
                if i + k + 3 <= n:
                    head.setdefault(data[i + k:i + k + 3], []).append(i + k)
            i += best_len
        else:
            if i + 3 <= n:
                head.setdefault(data[i:i + 3], []).append(i)
            lit.append(data[i])
            i += 1
    flush()
    out += bytes([0x80, 0, 0])
    return bytes(out)


def lz_unpack(src):
    out = bytearray()
    i = 0
    while True:
        t = src[i]
        i += 1
        if t < 0x80:
            out += src[i:i + t + 1]
            i += t + 1
        else:
            off = src[i] | (src[i + 1] << 8)
            i += 2
            if off == 0:
                return bytes(out)
            for _ in range((t & 0x7F) + 3):
                out.append(out[-off])


# --- asm output -----------------------------------------------------------------
def db_lines(data, per=16):
    data = bytes(data)
    lines = []
    for i in range(0, len(data), per):
        lines.append("    db " + ",".join("#%02X" % b for b in data[i:i + per]))
    return "\n".join(lines)


def selftest():
    assert m0_byte(1, 0) == 0x80 and m0_byte(0, 1) == 0x40
    assert m0_byte(15, 15) == 0xFF and m0_byte(8, 0) == 0x02
    assert m1_byte([1, 0, 0, 0]) == 0x80 and m1_byte([2, 0, 0, 0]) == 0x08
    assert m1_byte([3, 3, 3, 3]) == 0xFF
    import random
    for _ in range(20):
        d = bytes(random.choice([0, 0, 1, 2, 255]) for _ in range(3000))
        assert lz_unpack(lz_pack(d)) == d
    print("cpcgfx selftest ok")


if __name__ == "__main__":
    selftest()


# --- LZ2: denser packer with an optimal parse (format decoded by lz2_unpack)
#  0xxxxxxx          x+1 literal bytes follow
#  10llllll o        copy l+2 bytes (2..65) from dst-(o+1)          (o: 1 byte)
#  11llllll oo oo    copy l+3 bytes (3..65) from dst-offset          (l < 63)
#  11111111 oo oo e  copy e+66 bytes (66..321) from dst-offset; offset 0 = end
def _lz2_pack(data):
    data = bytes(data)
    n = len(data)
    INF = 1 << 30
    chains = {}
    best = [(0, 0, 0, 0)] * n
    for i in range(n - 1):
        key = data[i:i + 2]
        bs = bo = bl = ol = 0
        lim = min(321, n - i)
        for p in reversed(chains.get(key, [])[-256:]):
            off = i - p
            m = 2
            while m < lim and data[p + m] == data[i + m]:
                m += 1
            if off <= 256 and m > bs:
                bs, bo = min(m, 65), off
            if m > bl:
                bl, ol = m, off
                if m == lim:
                    break
        best[i] = (bs, bo, bl, ol)
        chains.setdefault(key, []).append(i)
    cost = [INF] * (n + 1)
    cost[n] = 0
    choice = [None] * (n + 1)
    for i in range(n - 1, -1, -1):
        c, ch = INF, None
        for k in range(1, min(128, n - i) + 1):
            v = 1 + k + cost[i + k]
            if v < c:
                c, ch = v, (0, k, 0)
        bs, bo, bl, ol = best[i]
        for L in range(2, bs + 1):
            v = 2 + cost[i + L]
            if v < c:
                c, ch = v, (1, L, bo)
        for L in range(3, bl + 1):
            v = (3 if L <= 65 else 4) + cost[i + L]
            if v < c:
                c, ch = v, (2, L, ol)
        cost[i], choice[i] = c, ch
    out = bytearray()
    i = 0
    while i < n:
        t, L, o = choice[i]
        if t == 0:
            out.append(L - 1)
            out += data[i:i + L]
        elif t == 1:
            out += bytes([0x80 | (L - 2), o - 1])
        elif L <= 65:
            out += bytes([0xC0 | (L - 3), o & 255, o >> 8])
        else:
            out += bytes([0xFF, o & 255, o >> 8, L - 66])
        i += L
    out += bytes([0xFF, 0, 0])
    return bytes(out)


def lz2_unpack(src):
    out = bytearray()
    i = 0
    while True:
        t = src[i]
        i += 1
        if t < 0x80:
            out += src[i:i + t + 1]
            i += t + 1
            continue
        if t < 0xC0:
            L, o = (t & 63) + 2, src[i] + 1
            i += 1
        else:
            o = src[i] | (src[i + 1] << 8)
            i += 2
            if t == 0xFF:
                if o == 0:
                    return bytes(out)
                L = src[i] + 66
                i += 1
            else:
                L = (t & 63) + 3
        for _ in range(L):
            out.append(out[-o])


def lz2_pack(data, cache_dir=None):
    """Packed bytes, cached by content (the optimal parse is slow)."""
    import hashlib
    data = bytes(data)
    if cache_dir:
        os.makedirs(cache_dir, exist_ok=True)
        p = os.path.join(cache_dir, hashlib.sha1(data).hexdigest() + ".lz2")
        if os.path.exists(p):
            with open(p, "rb") as f:
                return f.read()
    out = _lz2_pack(data)
    assert lz2_unpack(out) == data
    if cache_dir:
        with open(p, "wb") as f:
            f.write(out)
    return out
