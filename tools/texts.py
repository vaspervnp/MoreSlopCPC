"""All the words in MORE SLOP: HUD labels, ticker quips, cards, menu pages.

Output: build/texts.asm (lives in the #4000 bank, read by the Z80).
Strings: 0-terminated; \\x01 n = foreground pen, \\x02 n = background pen.
Special glyphs (copied from the ROM font): \\x80 heart, \\x81 empty box,
\\x82 full box, \\x83 lightning, \\x84 smiley, \\x85 sad face.
"""
import sys

FG = "\x01"
BG = "\x02"
HEART, BOX, FULL, ZAP, SMILE, SAD = "\x80", "\x81", "\x82", "\x83", "\x84", "\x85"


def fg(p):
    return FG + chr(p)


def bg(p):
    return BG + chr(p)


# ----------------------------------------------------------------- HUD
HUD_ROW0 = fg(1) + bg(0) + "SCORE" + " " * 26 + "HI"
HUD_ROW1 = fg(1) + bg(0) + "EP  WAVE   SLOP LEFT" + " " * 5 + "SHELF"

# ------------------------------------------------------------- ticker
MSGS_KILL = [
    "DELETED. NO REGRETS.",
    "HUMANITY +1",
    "THAT WAS NOT ART.",
    "REGENERATE THAT, BOT!",
    "CTRL+ALT+DELETE FOREVER",
    "+10 AUTHENTICITY",
    "SLOP-B-GONE!",
    "ONE LESS THING TO SCROLL PAST",
    "BACK TO THE TRAINING DATA!",
    "AS A HUMAN, I CAN ALLOW THIS.",
]
MSGS_MISS = [
    fg(2) + "SOLD TO A BOOMER FOR $49.99",
    fg(2) + "IT'S NOW TRENDING. GREAT.",
    fg(2) + "A CEO CALLED IT 'DISRUPTIVE'",
    fg(2) + "AUNTIE SHARED IT ON FACEBOOK",
    fg(2) + "IT GOT 2 MILLION LIKES. SIGH.",
    fg(2) + "NOW IN STOCK AT YOUR LOCAL SHOP",
]
MSGS_CLEAR = [
    "WAVE CLEARED! THE AI IS SULKING.",
    "WAVE CLEARED! TOUCH SOME GRASS.",
    "CLEAN! ...FOR NOW.",
]
MSGS_POPUP = [
    fg(2) + "POP-UP! ZAP IT 3 TIMES TO CLOSE",
    fg(2) + "THE AI WANTS YOUR FEEDBACK. NO.",
]
MSGS_BRO_IN = [
    fg(2) + "A CRYPTO-BRO IS AIRDROPPING IN!",
    fg(2) + "INCOMING BRO. POP HIS BUBBLE!",
]
MSGS_BRO = [
    fg(2) + "WAGMI! HE SOLD YOU A BUBBLE.",
    fg(2) + "'NOT FINANCIAL ADVICE' - SLOWED!",
    fg(2) + "HODL! YOU ARE NOW VERY SLOW.",
]

MSG = {
    "msg_get_ready": "GET READY. THE SLOPBOT IS WARMING UP...",
    "msg_wave": "WAVE ? - DESTROY ?? SLOP!",
    "msg_paused": fg(2) + "PAUSED. THE AI KEEPS TRAINING. P = GO",
    "msg_unpaused": "BACK TO WORK!",
    "msg_streak": "COMBO! SCORE X? - HUMAN AFTER ALL",
    "msg_coffee": "COFFEE BREAK! HUMAN CREATIVITY FLOWS",
    "msg_heart": "+1 LIFE. YOU TOUCHED GRASS.",
    "msg_life_lost": fg(2) + "THE SHELVES ARE FULL OF SLOP! -1 LIFE",
    "msg_no_lives": fg(2) + "YOU HAVE BEEN REPLACED BY A CHATBOT",
    "msg_popup_closed": "POP-UP DISMISSED. +30",
    "msg_banner": fg(2) + "CLICKBAIT BANNER! IT EATS YOUR ZAPS",
    "msg_banner_down": "FAKE NEWS DEBUNKED! +50",
    "msg_bro_left": "THE BRO LEFT TO BUY A LAMBO.",
    "msg_bubble": "BUBBLE POPPED. REKT! +25",
}

# ----------------------------------------------------- pop-up (episode 1)
POPUP_TITLE = fg(3) + bg(2) + "AI SAYS:   X"
POPUP_OK = fg(3) + bg(0) + "[OK]"
POPUP_TEXTS = [
    ["AS AN AI, I", "CANNOT ALLOW", "THE DESTRUC-", "TION OF ART."],
    ["I'M SORRY,", "THEMIS. I'M", "AFRAID I", "CAN'T DO IT."],
    ["PLEASE RATE", "THIS SLOP", "5 STARS TO", "CONTINUE."],
]

# --------------------------------------------- banners (episode 2), 20 chars
HEADLINES = [
    "THEMIS FIRED TODAY?!",
    " #4 WILL SHOCK YOU! ",
    "  DOCTORS HATE HIM  ",
    "  10X YOUR MINDSET  ",
    "AI WROTE 900 BOOKS! ",
    "YOU WON'T BELIEVE...",
    " SLOP IS THE FUTURE ",
    "CLICK HERE: FREE LOL",
]

# ----------------------------------------------------------------- cards
# (name, width in columns, y, height, [lines...]); a line is (y offset, text)
CARD_W = 19


def card(name, y, lines, pen_frame=2, pen_bg=0):
    h = 16 + 10 * len(lines)
    return dict(name=name, y=y, h=h, lines=lines, frame=pen_frame, bg=pen_bg)


def ep_card(n, title, sub, desc):
    lines = [fg(3) + bg(0) + "EPISODE %d" % n, fg(1) + title, fg(1) + sub, ""] + \
            [fg(3) + d for d in desc] + ["", fg(2) + "FIRE TO START"]
    return card("card_ep%d" % n, 44, lines)


CARDS = [
    ep_card(1, "THE HALLUCINATION", "FACTORY",
            ["ZAP 6-FINGER HANDS", "MANY-HEADED CATS,", "MELTED PORTRAITS.", "BEWARE AI POP-UPS!"]),
    ep_card(2, "THE CLICKBAIT", "EXPRESS",
            ["SHRED THE E-BOOKS", "AND THE CLICKBAIT.", "BANNERS BLOCK ZAPS", "- ZAP THEM DOWN!"]),
    ep_card(3, "THE CRYPTO", "GRAVEYARD",
            ["BURN APES & LAND.", "POP THE BUBBLES OF", "THE CRYPTO-BROS OR", "THEY'LL SLOW YOU!"]),
    card("card_clear", 80, [fg(3) + bg(0) + "WAVE CLEARED!", fg(1) + "THE AI IS", fg(1) + "RETRAINING..."]),
    card("card_over", 64, [fg(2) + bg(0) + "GAME OVER", "", fg(3) + "YOUR JOB HAS BEEN", fg(3) + "AUTOMATED.",
                           "", fg(1) + "FIRE FOR MENU"]),
    card("card_win", 56, [fg(3) + bg(0) + "CIVILIZATION", fg(3) + "SAVED!", "", fg(1) + "...FOR NOW. THE AI",
                          fg(1) + "IS NOW TRAINING ON", fg(1) + "YOUR WIN. AGAIN!", "", fg(2) + "FIRE: NEXT LOOP"]),
]

# ------------------------------------------------------------------- menu
DIFF_NAMES = ["TOUCH GRASS", "TERMINALLY ONLINE", "SINGULARITY"]
TXT_SELECT = fg(13) + bg(0) + "SELECT DIFFICULTY"
TXT_HISCORE = fg(10) + bg(0) + "HI-SCORE"
MENU_PAGES = [
    [fg(1) + bg(0) + "HOW TO PLAY", fg(14) + "ARROWS / A D: MOVE", fg(14) + "SPACE/FIRE: ZAP",
     fg(10) + "3 SLOP ON SHELF =", fg(10) + "ONE LIFE LOST!"],
    [fg(1) + bg(0) + "THE STORY", fg(14) + "THE AI WON'T STOP", fg(14) + "MAKING SLOP. ONLY",
     fg(14) + "THEMIS CAN SAVE US", fg(14) + "FROM THE FEED!"],
    [fg(1) + bg(0) + "POWER-UPS", fg(14) + "COFFEE: ZAPS ALL", fg(14) + "HEART: EXTRA LIFE",
     fg(10) + "6 HITS IN A ROW =", fg(10) + "SCORE MULTIPLIER"],
]
SCROLL = ("      ***  MORE SLOP  ***   THE AI HAS BEEN UP ALL NIGHT PRINTING SIX-FINGERED HANDS, "
          "THREE-HEADED CATS, 900 SELF-HELP E-BOOKS AND JPEGS OF BORED APES.  ONLY THEMIS AND HIS "
          "TRUSTY ZAPPER STAND BETWEEN CIVILIZATION AND THE INFINITE FEED.  PRESS 1-3 OR UP/DOWN TO "
          "PICK YOUR DIFFICULTY, H FOR HELP, FIRE TO START ...  NO NEURAL NETWORKS WERE HARMED IN "
          "THE MAKING OF THIS GAME (WELL, A FEW).  P PAUSES, ESC QUITS.  GREETINGS TO EVERYONE "
          "STILL WRITING THEIR OWN CODE BY HAND!        ")


def asm_str(s):
    """db line for a string with control/special codes."""
    parts = []
    buf = ""
    for ch in s:
        o = ord(ch)
        if 32 <= o < 127 and ch != '"':
            buf += ch
        else:
            if buf:
                parts.append('"%s"' % buf)
                buf = ""
            parts.append("%d" % o)
    if buf:
        parts.append('"%s"' % buf)
    parts.append("0")
    return "    db " + ",".join(parts)


def check(s, maxlen, what):
    n = 0
    i = 0
    while i < len(s):
        if s[i] in (FG, BG):
            i += 2
            continue
        n += 1
        i += 1
    if n > maxlen:
        sys.exit("%s too long (%d > %d): %r" % (what, n, maxlen, s))


def build(path):
    out = ["; generated by tools/texts.py - do not edit", ""]
    out.append("txt_hud_row0:")
    out.append(asm_str(HUD_ROW0))
    out.append("txt_hud_row1:")
    out.append(asm_str(HUD_ROW1))

    def table(name, msgs, maxlen=40):
        out.append("%s: db %d" % (name, len(msgs)))
        out.append("    dw " + ",".join("%s_%d" % (name, i) for i in range(len(msgs))))
        for i, m in enumerate(msgs):
            check(m, maxlen, name)
            out.append("%s_%d:" % (name, i))
            out.append(asm_str(m))

    table("msgs_kill", MSGS_KILL)
    table("msgs_miss", MSGS_MISS)
    table("msgs_clear", MSGS_CLEAR)
    table("msgs_popup", MSGS_POPUP)
    table("msgs_bro_in", MSGS_BRO_IN)
    table("msgs_bro", MSGS_BRO)
    for k, v in MSG.items():
        check(v, 40, k)
        out.append("%s:" % k)
        out.append(asm_str(v))
    # sanity: the patched positions
    assert MSG["msg_wave"].index("?") == 5 and MSG["msg_wave"][17:19] == "??"
    assert MSG["msg_streak"][14] == "?"

    out.append("txt_popup_title:")
    out.append(asm_str(POPUP_TITLE))
    out.append("txt_popup_ok:")
    out.append(asm_str(POPUP_OK))
    out.append("popup_texts:")
    for i, v in enumerate(POPUP_TEXTS):
        out.append("    dw " + ",".join("pt_%d_%d" % (i, j) for j in range(4)))
    for i, v in enumerate(POPUP_TEXTS):
        for j, line in enumerate(v):
            check(line, 12, "popup")
            out.append("pt_%d_%d:" % (i, j))
            out.append(asm_str(fg(1) + bg(0) + line))

    out.append("headlines: db %d" % len(HEADLINES))
    out.append("    dw " + ",".join("hdl_%d" % i for i in range(len(HEADLINES))))
    for i, h in enumerate(HEADLINES):
        assert len(h) == 20, h
        out.append("hdl_%d:" % i)
        out.append(asm_str(h))

    for c in CARDS:
        out.append("%s:" % c["name"])
        out.append("    db %d,0,%d,%d" % (CARD_W, c["y"], c["h"]))
        y, h = c["y"], c["h"]
        # frame then body, in strips of at most 16 lines
        out.append("    db 1,%d,%d,%d" % (y, h, c["frame"]))
        yy = y + 2
        while yy < y + h - 2:
            hh = min(16, y + h - 2 - yy)
            out.append("    db 1,%d,%d,%d" % (yy, hh, c["bg"] | 0x80))
            yy += hh
        for i, line in enumerate(c["lines"]):
            if not line:
                continue
            check(line, CARD_W - 1, c["name"])
            out.append("    db 2,%d : dw %s_l%d" % (y + 8 + 10 * i, c["name"], i))
        out.append("    db 0")
        for i, line in enumerate(c["lines"]):
            if line:
                out.append("%s_l%d:" % (c["name"], i))
                out.append(asm_str(line))

    out.append("diff_names: dw " + ",".join("dn_%d" % i for i in range(3)))
    for i, n in enumerate(DIFF_NAMES):
        out.append("dn_%d:" % i)
        out.append(asm_str(n))
    out.append("txt_select:")
    out.append(asm_str(TXT_SELECT))
    out.append("txt_hiscore:")
    out.append(asm_str(TXT_HISCORE))
    out.append("menu_pages: dw " + ",".join("mp_%d" % i for i in range(len(MENU_PAGES))))
    for i, page in enumerate(MENU_PAGES):
        out.append("mp_%d: dw %s,0" % (i, ",".join("mp_%d_%d" % (i, j) for j in range(len(page)))))
        for j, line in enumerate(page):
            check(line, 20, "menu page")
            out.append("mp_%d_%d:" % (i, j))
            out.append(asm_str(line))
    out.append("scroll_text:")
    out.append(asm_str(SCROLL))
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "build/texts.asm")
