"""Music for MORE SLOP: a tiny tracker format compiled to Z80 data.

Played by src/music.asm on the 50 Hz interrupt.

Pattern bytes
  #00-#5F  note (0 = C1), transposed by the order entry
  #60-#7F  set note length to (b - #5F) rows
  #80-#9F  set instrument
  #C0      rest   (silence for the current length)
  #C1      hold   (keep sounding for the current length)
  #FF      end of pattern
Order list: (dw pattern, db transpose)*, dw 0, dw loop-entry-or-0
Instrument: (ctl, val)* pairs; ctl bits 0-3 volume, bit 4 noise (val = noise
period, tone off), otherwise val = signed semitone offset. ctl #FF = jump
to step val.
"""
import os
import sys

NOTE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
N = 0x10  # noise flag in instrument ctl

INSTRUMENTS = {
    "silent": [(0, 0), (0xFF, 0)],
    "lead":   [(14, 0), (13, 0), (12, 0), (12, 0), (11, 0), (11, 0), (10, 0), (0xFF, 6)],
    "soft":   [(11, 0), (10, 0), (9, 0), (9, 0), (8, 0), (0xFF, 4)],
    "stab":   [(14, 0), (12, 0), (10, 0), (7, 0), (4, 0), (2, 0), (0, 0), (0xFF, 6)],
    "arpmaj":   [(12, 0), (12, 4), (12, 7), (11, 12), (11, 4), (11, 7), (10, 0), (10, 4),
               (10, 7), (9, 12), (9, 4), (9, 7), (0xFF, 6)],
    "arpmin":   [(12, 0), (12, 3), (12, 7), (11, 12), (11, 3), (11, 7), (10, 0), (10, 3),
               (10, 7), (9, 12), (9, 3), (9, 7), (0xFF, 6)],
    "bass":   [(15, 0), (14, 0), (13, 0), (12, 0), (11, 0), (10, 0), (9, 0), (0xFF, 6)],
    "pluck":  [(15, 12), (13, 0), (11, 0), (9, 0), (7, 0), (5, 0), (0xFF, 5)],
    "kick":   [(15, 0), (14, -5), (12, -10), (9, -15), (6, -20), (0, 0), (0xFF, 5)],
    "snare":  [(15 | N, 6), (13 | N, 8), (10 | N, 10), (7 | N, 12), (4 | N, 14), (0, 0), (0xFF, 5)],
    "hat":    [(9 | N, 1), (5 | N, 1), (0, 0), (0xFF, 2)],
    "wah":    [(13, 0), (13, 0), (12, 0), (12, -1), (12, -1), (11, 0), (11, 0), (11, -1),
               (11, -1), (0xFF, 5)],
}
INST_ORDER = list(INSTRUMENTS)

DRUM = {"K": ("kick", "C4"), "S": ("snare", "C4"), "H": ("hat", "C4")}


def note_num(tok):
    name = tok[0].upper()
    i = 1
    semi = NOTE[name]
    while i < len(tok) and tok[i] in "#b":
        semi += 1 if tok[i] == "#" else -1
        i += 1
    octave = int(tok[i:])
    n = (octave - 1) * 12 + semi
    assert 0 <= n < 96, tok
    return n


def compile_pattern(text):
    """Melodic pattern: 'C5:2 E5 @arpmaj G5:4 r - ...'. Returns (bytes, rows)."""
    out = bytearray()
    cur_len = None
    rows = 0
    for tok in text.split():
        if tok.startswith("@"):
            out.append(0x80 + INST_ORDER.index(tok[1:]))
            continue
        ln = None
        if ":" in tok:
            tok, l = tok.split(":")
            ln = int(l)
        if ln is not None and ln != cur_len:
            assert 1 <= ln <= 32
            out.append(0x5F + ln)
            cur_len = ln
        assert cur_len is not None, "length first: " + text
        if tok == "r":
            out.append(0xC0)
        elif tok == "-":
            out.append(0xC1)
        else:
            out.append(note_num(tok))
        rows += cur_len
    out.append(0xFF)
    return bytes(out), rows


def compile_drums(text):
    """Drum pattern, one char per row: K kick, S snare, H hat, . nothing."""
    text = text.replace(" ", "")
    out = bytearray()
    cur_len = None
    cur_inst = None
    i = 0
    while i < len(text):
        c = text[i]
        j = i + 1
        while j < len(text) and text[j] == ".":
            j += 1
        ln = j - i
        if ln != cur_len:
            out.append(0x5F + ln)
            cur_len = ln
        if c == ".":
            out.append(0xC1)
        else:
            inst, note = DRUM[c]
            if inst != cur_inst:
                out.append(0x80 + INST_ORDER.index(inst))
                cur_inst = inst
            out.append(note_num(note))
        i = j
    out.append(0xFF)
    return bytes(out), len(text)


# ---------------------------------------------------------------- the songs
# Each song: speed (frames per row), patterns, and per-channel orders
# [(pattern, transpose), ...], loop index (None = play once).

SONGS = {}

# ------------------------------------------------------------------ menu
SONGS["menu"] = dict(
    speed=6,
    pats={
        "m1": "@lead E5:2 G5 C6:4 B5:2 G5 E5 G5",
        "m2": "D5:2 G5 B5:4 A5:2 G5 D5 B4",
        "m3": "C5:2 E5 A5:4 G5:2 E5 C5 E5",
        "m4": "F5:4 A5 G5:2 F5 E5 D5",
        "m5": "E5:2 G5 C6:4 D6:2 C6 B5 C6",
        "m6": "D6:4 B5 G5 r",
        "m7": "A5:2 C6 A5 F5 G5:4 A5",
        "m8": "G5:2 F5 E5 D5 B4:8",
        "c1": "@arpmin A4:16", "c2": "@arpmaj F4:16", "c3": "@arpmaj C5:16", "c4": "@arpmaj G4:16",
        "n1": "@lead A5:3 G5 E5:2 A5:3 G5 E5:2",
        "n2": "F5:3 E5 C5:2 F5:3 E5 C5:2",
        "n3": "E5:3 D5 C5:2 G5:4 E5",
        "n4": "D5:2 E5 F5 G5 A5 B5 C6:4",
        "bs": "@bass C2:2 C3 C2 C3 C2 C3 C2 C3",
        "bs2": "@pluck C2:2 C3 G2 C3 C2 C3 G2 A#2",
        "dr": "D:K.H.S.H.K.KHS.HH",
        "df": "D:K.H.S.H.K.S.SSSS",
    },
    A=[("m1", 0), ("m2", 0), ("m3", 0), ("m4", 0), ("m5", 0), ("m6", 0), ("m7", 0), ("m8", 0),
       ("c1", 0), ("c2", 0), ("c3", 0), ("c4", 0), ("n1", 0), ("n2", 0), ("n3", 0), ("n4", 0)],
    B=[("bs", 0), ("bs", -5), ("bs", -3), ("bs", -7), ("bs", 0), ("bs", -5), ("bs", -7), ("bs", -5),
       ("bs2", -3), ("bs2", -7), ("bs2", 0), ("bs2", -5), ("bs", -3), ("bs", -7), ("bs", 0), ("bs", -5)],
    C=[("dr", 0)] * 3 + [("df", 0)] + [("dr", 0)] * 3 + [("df", 0)]
      + [("dr", 0)] * 3 + [("df", 0)] + [("dr", 0)] * 3 + [("df", 0)],
    loop=0,
)

# ------------------------------------------------------- ep1: the factory
SONGS["ep1"] = dict(
    speed=5,
    pats={
        "a1": "@stab A4:2 C5 E5 A5 G5 E5 C5 E5",
        "a2": "A4:2 C5 E5 A5 B5 A5 G5 E5",
        "a3": "F4:2 A4 C5 F5 E5 C5 A4 C5",
        "a4": "G4:2 B4 D5 G5 F5 D5 B4 D5",
        "b1": "@lead E5:4 A5 G5:2 E5 C5:4",
        "b2": "D5:2 E5 C5:4 A4:8",
        "b3": "F5:4 A5 D6 C6",
        "b4": "B5:4 G#5 E5 r",
        "bs": "@bass A1:1 r A2 A1 r A2 A1 A2 A1 r A2 A1 r A2 G1 G2",
        "dr": "D:K.H.S.HKK.H.S.HH",
        "dx": "D:K.H.S.HKK.HSSKSS",
    },
    A=[("a1", 0), ("a2", 0), ("a3", 0), ("a4", 0), ("a1", 0), ("a2", 0), ("a3", 0), ("a4", 0),
       ("b1", 0), ("b2", 0), ("b3", 0), ("b4", 0), ("b1", 0), ("b2", 0), ("b3", 0), ("b4", 0)],
    B=[("bs", 0), ("bs", 0), ("bs", -4), ("bs", -2)] * 2
      + [("bs", 0), ("bs", 0), ("bs", 5), ("bs", 7)] * 2,
    C=[("dr", 0), ("dr", 0), ("dr", 0), ("dx", 0)] * 4,
    loop=0,
)

# --------------------------------------------------- ep2: clickbait funk
SONGS["ep2"] = dict(
    speed=5,
    pats={
        "f1": "@stab D5:1 r F5 r:3 A5:2 G5 F5 D5:4",
        "f2": "B4:1 r D5 r:3 G5:2 F5 D5 B4:4",
        "f5": "@lead A5:4 C6 A5:2 G5 F5:4",
        "f6": "G5:4 E5 C5 E5",
        "f7": "D5:2 G5 B5:4 A5:2 G5 D5:4",
        "f8": "C#5:4 E5 A5:8",
        "bs": "@pluck D2:2 r:1 D3 r:2 A2 C3 D3 r A2",
        "dr": "D:K.HKS.H.HKK.S.HK",
        "dx": "D:K.HKS.H.HKK.SSSS",
    },
    A=[("f1", 0), ("f2", 0), ("f1", 0), ("f2", 0), ("f5", 0), ("f6", 0), ("f7", 0), ("f8", 0)],
    B=[("bs", 0), ("bs", 5), ("bs", 0), ("bs", 5), ("bs", 3), ("bs", -2), ("bs", 5), ("bs", 7)],
    C=[("dr", 0), ("dr", 0), ("dr", 0), ("dx", 0)] * 2,
    loop=0,
)

# ----------------------------------------------- ep3: the crypto graveyard
SONGS["ep3"] = dict(
    speed=4,
    pats={
        "g1": "@stab E5:2 G5 B5 E6 B5 G5 E5 G5",
        "g2": "E5:2 G5 C6 E6 C6 G5 E5 G5",
        "g3": "E5:2 A5 C6 E6 C6 A5 E5 A5",
        "g4": "D#5:2 F#5 B5 D#6 B5 F#5 D#5 F#5",
        "h1": "@lead B5:6 A5:2 G5:4 F#5",
        "h2": "E5:6 G5:2 C6:8",
        "h3": "A5:4 C6 B5 A5",
        "h4": "F#5:4 D#5 B4:8",
        "bs": "@bass E2:1 E2 E3 E2 E2 E3 E2 E3 E2 E2 E3 E2 E2 E3 D3 E3",
        "dr": "D:K.HKS.HKK.HKS.KS",
        "dx": "D:K.HKS.HKSSSSKKSS",
    },
    A=[("g1", 0), ("g2", 0), ("g3", 0), ("g4", 0), ("h1", 0), ("h2", 0), ("h3", 0), ("h4", 0)],
    B=[("bs", 0), ("bs", -4), ("bs", -7), ("bs", -5), ("bs", 0), ("bs", -4), ("bs", -7), ("bs", -5)],
    C=[("dr", 0), ("dr", 0), ("dr", 0), ("dx", 0)] * 2,
    loop=0,
)

# ---------------------------------------------------------------- jingles
SONGS["clear"] = dict(
    speed=4,
    pats={"l": "@lead C5:2 E5 G5 C6:4 G5:2 C6:4",
          "b": "@bass C2:4 G2 C3:8",
          "d": "D:K.K.S.K.K.S.SSSS"},
    A=[("l", 0)], B=[("b", 0)], C=[("d", 0)], loop=None)

SONGS["over"] = dict(  # the sad trombone
    speed=7,
    pats={"l": "@wah G4:3 F#4 F4 E4:12",
          "b": "@wah G3:3 F#3 F3 E3:12",
          "d": "D:K..K..K..S..........."},
    A=[("l", 0)], B=[("b", 0)], C=[("d", 0)], loop=None)

SONGS["lost"] = dict(
    speed=3,
    pats={"l": "@lead C6:2 B5 A#5 A5 G#5 G5:6",
          "b": "@bass C3:2 B2 A#2 A2 G#2 G2:6",
          "d": "D:S.S.S.S.S.K....."},
    A=[("l", 0)], B=[("b", 0)], C=[("d", 0)], loop=None)

SONG_ORDER = ["menu", "ep1", "ep2", "ep3", "clear", "over", "lost"]


def per(note):
    n = note_num(note)
    f = 440.0 * 2 ** ((n - 45) / 12.0)
    return int(round(1000000.0 / (16 * f)))


# Sound effects: list of frames (volume, tone period or None, noise period or None)
def sfx_defs():
    S = {}
    S["zap"] = [(14, 420, 3), (14, 300, 2), (13, 220, None), (12, 160, None), (11, 120, None),
                (9, 90, None), (7, 70, None), (5, 60, None), (3, 50, None)]
    S["boom"] = [(15, 900, 4), (15, 1200, 6), (14, 1500, 8), (13, 1900, 10)] + \
                [(12 - i, None, 12 + i * 2) for i in range(10)]
    S["sold"] = [(13, per("B6"), 1), (13, per("B6"), None), (12, per("B6"), None)] + \
                [(13 - i, per("E7"), None) for i in range(11)]
    S["popup"] = [(13, per("E5"), None)] * 4 + [(0, None, None)] + \
                 [(13 - i // 2, per("B4"), None) for i in range(12)]
    S["blip"] = [(12, per("C6"), None), (10, per("G6"), None), (6, per("C7"), None)]
    S["power"] = [(13, per(n), None) for n in ["C5", "C5", "E5", "E5", "G5", "G5", "C6", "C6",
                                                 "E6", "E6", "G6", "G6", "C7", "C7"]] + \
                 [(10 - i, per("C7"), None) for i in range(8)]
    S["thud"] = [(13, 2000, 20), (10, 2400, 24), (7, 2800, 28), (4, None, 31)]
    S["pop"] = [(12, 70, None), (12, 50, None), (10, 36, None), (6, 28, None), (3, 24, None)]
    S["start"] = [(13, per(n), None) for n in ["C5", "C5", "G5", "G5", "C6", "C6", "E6", "E6",
                                                 "G6", "G6", "G6", "G6"]] + \
                 [(11 - i, per("C7"), None) for i in range(10)]
    return S


SFX_ORDER = ["zap", "boom", "sold", "popup", "blip", "power", "thud", "pop", "start"]


def sfx_asm():
    S = sfx_defs()
    out = ["sfx_tab: dw " + ",".join("sfxd_" + k for k in SFX_ORDER)]
    for k in SFX_ORDER:
        b = []
        for vol, tone, noise in S[k]:
            ctl = vol & 15
            if noise is not None:
                ctl |= 0x10
            if tone is None:
                ctl |= 0x20
            t = tone or 0
            b += [ctl, t & 0xFF, t >> 8, noise or 0]
        b.append(0xFF)
        out.append("sfxd_%s: db %s" % (k, ",".join("#%02X" % v for v in b)))
    return out


def build(path):
    out = ["; generated by tools/music.py - do not edit", ""]
    # period table: 96 notes from C1, AY clocked at 1 MHz
    per = []
    for n in range(96):
        f = 440.0 * 2 ** ((n - 45) / 12.0)  # n=45 -> A4
        per.append(min(4095, int(round(1000000.0 / (16 * f)))))
    out.append("mus_periods:")
    for i in range(0, 96, 12):
        out.append("    dw " + ",".join(str(p) for p in per[i:i + 12]))
    out.append("mus_insts:")
    out.append("    dw " + ",".join("inst_" + k for k in INST_ORDER))
    for k in INST_ORDER:
        b = []
        for ctl, val in INSTRUMENTS[k]:
            b += [ctl & 0xFF, val & 0xFF]
        out.append("inst_%s: db %s" % (k, ",".join("#%02X" % v for v in b)))
    total = 0
    for sname in SONG_ORDER:
        s = SONGS[sname]
        out.append("")
        out.append("song_%s:" % sname)
        out.append("    db %d" % s["speed"])
        out.append("    dw song_%s_A,song_%s_B,song_%s_C" % (sname, sname, sname))
        rows_per_ch = {}
        pat_rows = {}
        for pn, txt in s["pats"].items():
            if txt.startswith("D:"):
                data, rows = compile_drums(txt[2:])
            else:
                data, rows = compile_pattern(txt)
            pat_rows[pn] = rows
            total += len(data)
            out.append("pat_%s_%s:" % (sname, pn))
            out.append("    db " + ",".join("#%02X" % v for v in data))
        for ch in "ABC":
            out.append("song_%s_%s:" % (sname, ch))
            rows = 0
            for pn, tr in s[ch]:
                out.append("    dw pat_%s_%s : db %d" % (sname, pn, tr & 0xFF))
                rows += pat_rows[pn]
            rows_per_ch[ch] = rows
            if s["loop"] is None:
                out.append("    dw 0,0")
            else:
                out.append("    dw 0,song_%s_%s+%d" % (sname, ch, 3 * s["loop"]))
        if len(set(rows_per_ch.values())) != 1:
            sys.exit("song %s: channels have different lengths %s" % (sname, rows_per_ch))
    out.append("")
    for i, sname in enumerate(SONG_ORDER):
        out.append("SNG_%s equ %d" % (sname.upper(), i))
    out.append("mus_songs: dw " + ",".join("song_" + s for s in SONG_ORDER))
    out += sfx_asm()
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")
    print("music: %d songs, %d pattern bytes" % (len(SONG_ORDER), total))


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "build/music_data.asm")
