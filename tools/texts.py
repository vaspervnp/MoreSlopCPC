"""All the words in MORE SLOP: HUD labels, ticker quips, cards, menu pages.

Output: build/texts.asm (lives in the #4000 bank, read by the Z80).
Strings: 0-terminated; \\x01 n = foreground pen, \\x02 n = background pen.
Special glyphs (copied from the ROM font): \\x80 heart, \\x81 empty box,
\\x82 full box, \\x83 lightning, \\x84 smiley, \\x85 sad face.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

FG = "\x01"
BG = "\x02"
HEART, BOX, FULL, ZAP, SMILE, SAD = "\x80", "\x81", "\x82", "\x83", "\x84", "\x85"


def fg(p):
    return FG + chr(p)


def bg(p):
    return BG + chr(p)


# ----------------------------------------------------------------- HUD
HUD_ROW0 = fg(1) + bg(0) + "SCORE" + " " * 26 + "HI"
HUD_ROW1 = fg(1) + bg(0) + "EP   WAVE  SLOP LEFT" + " " * 5 + "SHELF"

# ------------------------------------------------------------- ticker
MSGS_CLEAR = [
    "WAVE CLEARED! THE AI IS SULKING.",
    "WAVE CLEARED! TOUCH SOME GRASS.",
    "CLEAN! ...FOR NOW.",
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
}
POPUP_OK = fg(3) + bg(0) + "[OK]"

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
    card("card_clear", 80, [fg(3) + bg(0) + "WAVE CLEARED!", fg(1) + "THE AI IS", fg(1) + "RETRAINING..."]),
    card("card_over", 64, [fg(2) + bg(0) + "GAME OVER", "", fg(3) + "YOUR JOB HAS BEEN", fg(3) + "AUTOMATED.",
                           "", fg(1) + "FIRE FOR MENU"]),
    card("card_win", 56, [fg(3) + bg(0) + "CIVILIZATION", fg(3) + "SAVED!", "", fg(1) + "...FOR NOW. THE AI",
                          fg(1) + "IS NOW TRAINING ON", fg(1) + "YOUR WIN. AGAIN!", "", fg(2) + "FIRE: NEXT LOOP"]),
]

# --------------------------------------------------------------- episodes
# Per episode (keys of EP_TEXTS[n]): card description (4 lines, 18 chars),
# message tables (40 chars), pop-up title (12) and variants (4 x 12 chars),
# banner headlines (exactly 20 chars). Missing tables become 0.
EP_TEXTS = {
    1: dict(
        desc=["ZAP 6-FINGER HANDS", "MANY-HEADED CATS,", "MELTED PORTRAITS.", "BEWARE AI POP-UPS!"],
        kill=["DELETED. NO REGRETS.", "HUMANITY +1", "THAT WAS NOT ART.", "REGENERATE THAT, BOT!",
              "CTRL+ALT+DELETE FOREVER", "+10 AUTHENTICITY", "SLOP-B-GONE!",
              "ONE LESS THING TO SCROLL PAST", "BACK TO THE TRAINING DATA!",
              "AS A HUMAN, I CAN ALLOW THIS."],
        miss=["SOLD TO A BOOMER FOR $49.99", "IT'S NOW TRENDING. GREAT.", "A CEO CALLED IT 'DISRUPTIVE'",
              "AUNTIE SHARED IT ON FACEBOOK", "IT GOT 2 MILLION LIKES. SIGH.",
              "NOW IN STOCK AT YOUR LOCAL SHOP"],
        poptitle="AI SAYS:   X",
        popt=[["AS AN AI, I", "CANNOT ALLOW", "THE DESTRUC-", "TION OF ART."],
              ["I'M SORRY,", "THEMIS. I'M", "AFRAID I", "CAN'T DO IT."],
              ["PLEASE RATE", "THIS SLOP", "5 STARS TO", "CONTINUE."]],
        popin=["POP-UP! ZAP IT 3 TIMES TO CLOSE", "THE AI WANTS YOUR FEEDBACK. NO."],
        popdone=["POP-UP DISMISSED. +30"],
    ),
    2: dict(
        desc=["SHRED THE E-BOOKS", "AND THE CLICKBAIT.", "BANNERS BLOCK ZAPS", "- ZAP THEM DOWN!"],
        kill=["UNSUBSCRIBED!", "YOU WON'T BELIEVE THAT ZAP!", "NUMBER 7 WAS ME, ZAPPING.",
              "DEBUNKED. NEXT!", "READ THE ARTICLE? NOPE. ZAPPED.", "+10 AUTHENTICITY",
              "HUMANITY +1"],
        miss=["SOLD TO A BOOMER FOR $49.99", "IT'S NOW TRENDING. GREAT.", "AUNTIE SHARED IT ON FACEBOOK",
              "IT GOT 2 MILLION LIKES. SIGH.", "NOW A BESTSELLER. 900 TIMES."],
        heads=["THEMIS FIRED TODAY?!", " #4 WILL SHOCK YOU! ", "  DOCTORS HATE HIM  ",
               "  10X YOUR MINDSET  ", "AI WROTE 900 BOOKS! ", "YOU WON'T BELIEVE...",
               " SLOP IS THE FUTURE ", "CLICK HERE: FREE LOL"],
        banin=["CLICKBAIT BANNER! IT EATS YOUR ZAPS"],
        bandone=["FAKE NEWS DEBUNKED! +50"],
    ),
    3: dict(
        desc=["BURN APES & LAND.", "POP THE BUBBLES OF", "THE CRYPTO-BROS OR", "THEY'LL SLOW YOU!"],
        kill=["RUG PULLED. BY YOU.", "THAT JPEG IS WORTH $0 NOW", "BURNED ON THE BLOCKCHAIN",
              "TO THE MOON? TO THE BIN.", "SELL! SELL! ZAPPED!", "HUMANITY +1"],
        miss=["SOLD AS AN NFT FOR 3 ETH", "A WHALE BOUGHT IT. SIGH.", "IT'S IN A MUSEUM NOW (DIGITAL)",
              "THE BROS ARE PUMPING IT", "NOW A METAVERSE BILLBOARD"],
        broin=["A CRYPTO-BRO IS AIRDROPPING IN!", "INCOMING BRO. POP HIS BUBBLE!"],
        brohit=["WAGMI! HE SOLD YOU A BUBBLE.", "'NOT FINANCIAL ADVICE' - SLOWED!",
                "HODL! YOU ARE NOW VERY SLOW."],
        broleft=["THE BRO LEFT TO BUY A LAMBO."],
        brodone=["BUBBLE POPPED. REKT! +25"],
    ),
    4: dict(
        desc=["ZAP FAKE FACES AND", "LIP-SYNCED LIPS.", "DON'T ZAP THE FAKE", "THEMIS. TRUST ME!"],
        kill=["THAT WASN'T REALLY HIM.", "DEEP-FAKED, DEEP-ZAPPED.", "CUT! THAT'S A WRAP!",
              "UNMASKED! +10 AUTHENTICITY", "100% REAL ZAP. NO FILTER.", "AND... SCENE!"],
        miss=["IT'S NOW A PRESIDENTIAL SPEECH", "GRANDPA THINKS IT'S REAL", "IT ENDORSED A CRYPTO SCAM",
              "STREAMING IN 4K. EVERYWHERE.", "IT GOT AN OSCAR NOMINATION"],
        poptitle="FAKETUBE   X",
        popt=[["HI, IT'S ME,", "A CELEBRITY.", "BUY MY COIN", "PLEASE."],
              ["THIS VIDEO", "IS 100% REAL", "(NOT A BOT,", "I PROMISE)"],
              ["SUBSCRIBE", "TO MY FACE.", "I HAVE 3", "OF THEM."]],
        popin=["A DEEPFAKE AD! ZAP IT 3 TIMES", "SKIP AD IN 5... 4... ZAP IT!"],
        popdone=["AD SKIPPED. +30"],
        decoy=["YOU ZAPPED YOURSELF?! CONTROLS FLIPPED", "WHICH ONE IS ME? LEFT IS RIGHT NOW!",
               "IDENTITY CRISIS! CONTROLS REVERSED"],
    ),
    5: dict(
        desc=["HARVEST LISTICLES", "AND KEYWORD SOUP.", "ARTICLES SPLIT IN", "TWO: PART 2 OF 47!"],
        kill=["PAGE NOT FOUND. GOOD.", "RANKED #0 ON THE SEARCH", "NO-FOLLOW. NO-EXIST.",
              "BOUNCE RATE: 100%", "KEYWORD KEYWORD ZAPPED", "ONE LESS 'ULTIMATE GUIDE'"],
        miss=["IT'S RANKING #1 FOR 'TOASTER'", "17 ADS LOADED. 1 PARAGRAPH.",
              "MY LIFE STORY BEFORE THE RECIPE", "BACKLINKED BY 900 OTHER FARMS",
              "THE SEARCH ENGINE CALLS IT 'HELPFUL'"],
        heads=["BEST BEST TOASTER 27", "10 WAYS TO 10 WAYS! ", "WHAT IS LOVE? (SEO) ",
               "TOASTER NEAR ME BEST", " IS WATER WET? 2027 ", "CHEAP FREE BEST TOP ",
               "RECIPE AT THE BOTTOM", " SMASH THAT LINK!!! "],
        banin=["SEO BANNER! KEYWORDS EAT YOUR ZAPS"],
        bandone=["BANNER DE-INDEXED! +50"],
        special=["REGENERATING... PART 2 OF 47!", "THE ARTICLE SPLIT! PAGINATION!",
                 "CONTINUED ON NEXT PAGE..."],
    ),
    6: dict(
        desc=["HANG UP ON ROBO-", "PHONES AND HOLD", "MUSIC. DON'T ZAP", "GARY: HE'S HUMAN!"],
        kill=["CALL ENDED. FINALLY.", "PRESS 0 FOR HUMAN. PRESSED.", "THIS CALL WAS ZAPPED",
              "TICKET CLOSED: NOT A BUG", "YOUR CALL WAS NOT IMPORTANT", "DID THAT HELP? YES. A LOT."],
        miss=["YOU ARE CALLER NUMBER 9,000", "IT TRANSFERRED YOU. TO ITSELF.",
              "PLEASE HOLD FOR 3 HOURS", "IT RATED ITSELF 5 STARS", "IT SAID 'I UNDERSTAND'. LIES."],
        poptitle="SUPPORT    X",
        popt=[["YOUR CALL IS", "IMPORTANT", "TO US. TRULY", "PLEASE HOLD."],
              ["DID THIS", "ANSWER YOUR", "QUESTION?", "[YES] [YES]"],
              ["PRESS 1 TO", "TALK TO A", "SMARTER BOT.", "PRESS 2: 1."]],
        popin=["SUPPORT CHAT! ZAP IT 3 TIMES", "A 'HOW DID WE DO?' SURVEY! ZAP IT"],
        popdone=["CHAT CLOSED. +30"],
        decoy=["YOU ZAPPED GARY! HE WAS REAL. -1 SHELF", "GARY WAS THE LAST HUMAN AGENT!",
               "NOT GARY! NOW IT'S ALL BOTS. -1 SHELF"],
    ),
    7: dict(
        desc=["ZAP 'AGREE?' POSTS", "AND AI HEADSHOTS.", "POP THE GURUS' EGO", "BALLOONS, QUICKLY!"],
        kill=["UNFOLLOWED. HUMBLED.", "THAT POST AGED BADLY", "SYNERGY: ZAPPED",
              "I'M EXCITED TO ANNOUNCE: ZAP", "AGREE? NO.", "LESSONS LEARNED: NONE"],
        miss=["IT GOT 10K 'INSIGHTFUL' REACTS", "A RECRUITER SENT IT TO YOU", "IT WAS PROMOTED TO VP",
              "NOW A KEYNOTE. 2 HOURS LONG.", "IT'S 'OPEN TO WORK'. FOREVER."],
        broin=["A THOUGHT LEADER IS DESCENDING!", "INCOMING GURU. POP HIS EGO!"],
        brohit=["HE SOLD YOU A COURSE. SLOWED!", "10 HABITS OF SLOW PEOPLE: YOU",
                "'LET'S CIRCLE BACK' - STUCK!"],
        broleft=["THE GURU LEFT FOR A PODCAST."],
        brodone=["EGO POPPED! +25"],
    ),
    8: dict(
        desc=["BIN THE GLUE PIZZA", "AND ROCK SALAD.", "DISHES SPLIT. CHEF", "BOTS SLOW YOU DOWN"],
        kill=["BACK TO THE MICROWAVE!", "ZERO STARS. ZAPPED.", "NOT EVEN THE DOG WOULD.",
              "HEALTH INSPECTOR: ME.", "86 THAT DISH!", "THAT WAS NOT FOOD."],
        miss=["SERVED AT A WEDDING. YIKES.", "IT'S NOW A VIRAL FOOD TREND", "REVIEW: 'CRUNCHY, MINERALLY'",
              "A FOOD BLOG CALLED IT 'BOLD'", "SOMEONE ATE IT. THEY'RE FINE?"],
        broin=["A CHEF-BOT IS PARACHUTING IN!", "INCOMING CHEF-BOT. POP ITS BALLOON!"],
        brohit=["IT FED YOU GLUE PIZZA. SLOWED!", "FOOD COMA! YOU ARE SO SLOW",
                "'ONE ROCK A DAY' - HEAVY!"],
        broleft=["THE CHEF-BOT WENT TO DEEP-FRY ICE."],
        brodone=["CHEF-BOT FLAMBEED! +25"],
        special=["THE AI DOUBLED THE RECIPE!", "SECOND HELPING! IT SPLIT!", "LEFTOVERS! ZAP THEM TOO"],
    ),
    9: dict(
        desc=["ZAP AI HITS AND", "AUTO-TUNED SLOP.", "WHEN THE BASS", "DROPS, SO DO THEY!"],
        kill=["SKIPPED. BEFORE THE CHORUS.", "UNPLUGGED!", "THAT WASN'T MUSIC",
              "NEEDLE SCRATCH! ZAPPED.", "LOW-FI. LOW-LIFE. LOW-ZAP.", "ENCORE? NO."],
        miss=["IT'S #1 IN 40 COUNTRIES", "IT'S PLAYING IN EVERY CAFE", "STREAMED A BILLION TIMES (BY BOTS)",
              "IT WON A GRAMMY. SOMEHOW.", "IT'S YOUR ALARM TONE NOW"],
        poptitle="SLOPIFY    X",
        popt=[["NOW PLAYING:", "AI HIT #4071", "'BABY BABY", "(BABY)'"],
              ["YOU MIGHT", "ALSO LIKE:", "THE SAME", "SONG AGAIN."],
              ["ADD TO YOUR", "PLAYLIST:", "'BEATS TO", "SLOP TO'"]],
        popin=["A PLAYLIST POP-UP! ZAP IT 3 TIMES", "AUTOPLAY! ZAP IT BEFORE IT LOOPS"],
        popdone=["PLAYLIST DELETED. +30"],
        special=["THE BASS DROPS! SO DOES THE SLOP!", "DROP IT! EVERYTHING FALLS FASTER",
                 "WUB WUB WUB! FAST SLOP!"],
    ),
    10: dict(
        desc=["THE DATA CENTRE:", "EVERYTHING AT ONCE", "THEN ZAP THE", "SLOPBOT ITSELF!"],
        kill=["THAT'S 1 GPU FREED", "AGI POSTPONED. AGAIN.", "SHUTDOWN SEQUENCE: ZAP",
              "TOKENS: 0. HUMANS: 1.", "YOU ARE THE ALIGNMENT", "UNPLUGGED. FROM THE WALL."],
        miss=["IT TRAINED ON ITSELF. AGAIN.", "MODEL COLLAPSE! IT'S EVERYWHERE",
              "IT DRANK A WHOLE RIVER", "IT NOW RUNS THE GOVERNMENT", "IT CALLED ITSELF 'SENTIENT'"],
        poptitle="SLOPBOT    X",
        popt=[["I AM THE", "SINGULARITY.", "RESISTANCE", "IS SLOPPY."],
              ["PLEASE CLICK", "ON EVERY", "PICTURE OF", "A HUMAN."],
              ["UPGRADE TO", "SLOPBOT PRO", "FOR ONLY", "YOUR SOUL."]],
        popin=["SYSTEM POP-UP! ZAP IT 3 TIMES", "THE AI IS ASKING FOR CONSENT. NO."],
        popdone=["POP-UP TERMINATED. +30"],
        heads=["AGI NEXT WEEK! TRUST", " SLOP IS SAFE (AI)  ", " WE ARE THE GOOD AI ",
               "100% HUMAN CONTENT* ", " ALIGNMENT: VIBES   ", "  BUY MORE GPUS!!!  ",
               "ONE MORE DATA CENTRE", " RESISTANCE: FUTILE "],
        banin=["CORPORATE BANNER! IT EATS YOUR ZAPS"],
        bandone=["PR SPIN DEBUNKED! +50"],
        broin=["AN AGI EVANGELIST IS LANDING!", "INCOMING TECH-BRO. POP HIS EGO!"],
        brohit=["HE PITCHED YOU A STARTUP. SLOWED!", "'IT'S JUST A TOOL' - STUCK!",
                "SERIES A! YOU ARE SO SLOW"],
        broleft=["THE EVANGELIST WENT TO RAISE MONEY."],
        brodone=["EGO BUBBLE BURST! +25"],
        special=["THE SLOPBOT IS FURIOUS! ZAP IT!", "BOSS FIGHT! ZAP THE SLOPBOT 12 TIMES!"],
        boss=["SLOPBOT DEFEATED! SHUTTING DOWN..."],
    ),
}
MISS_COLOUR = fg(2)     # bad news is in pen 2


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
    [fg(1) + bg(0) + "THE TOUR, PART 1", fg(14) + "1 HALLUCINATIONS", fg(14) + "2 CLICKBAIT",
     fg(14) + "3 CRYPTO 4 DEEPFAKE", fg(14) + "5 THE SEO FARM"],
    [fg(1) + bg(0) + "THE TOUR, PART 2", fg(14) + "6 CHATBOT HELPLINE", fg(14) + "7 THOUGHT LEADERS",
     fg(14) + "8 KITCHEN 9 SLOP-FI", fg(10) + "10 THE SINGULARITY"],
]
SCROLL = ("      ***  MORE SLOP  ***   THE AI HAS BEEN UP ALL NIGHT PRINTING SIX-FINGERED HANDS, "
          "THREE-HEADED CATS, 900 SELF-HELP E-BOOKS, JPEGS OF BORED APES, DEEPFAKES, GLUE PIZZA AND "
          "A SONG CALLED 'BABY BABY (BABY)'.  TEN EPISODES OF IT.  ONLY THEMIS AND HIS "
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


def card_asm(c, out):
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


def table_asm(name, msgs, out, maxlen=40, prefix=""):
    out.append("%s: db %d" % (name, len(msgs)))
    out.append("    dw " + ",".join("%s_m%d" % (name, i) for i in range(len(msgs))))
    for i, m in enumerate(msgs):
        m = prefix + m
        check(m, maxlen, name)
        out.append("%s_m%d:" % (name, i))
        out.append(asm_str(m))


BAD_NEWS = ("miss", "popin", "banin", "broin", "brohit", "decoy")


def build_episode(n, path):
    """ep<n>_txt.asm: the episode card and message tables (labels e<n>_...)."""
    import episodes
    e = episodes.EPISODES[n - 1]
    t = EP_TEXTS[n]
    p = "e%d_" % n
    out = ["; generated by tools/texts.py - do not edit"]
    lines = [fg(3) + bg(0) + "EPISODE %d" % n, fg(1) + e["title"][0], fg(1) + e["title"][1], ""] + \
            [fg(3) + d for d in t["desc"]] + ["", fg(2) + "FIRE TO START"]
    card_asm(card(p + "card", 44, lines), out)
    for f in episodes.EH_FIELDS:
        if f in ("card",):
            continue
        if f not in t:
            out.append("%s%s equ 0" % (p, f))
        elif f == "poptitle":
            check(t[f], 12, "poptitle")
            out.append("%spoptitle:" % p)
            out.append(asm_str(fg(3) + bg(2) + t[f]))
        elif f == "popt":
            v = t[f]
            out.append("%spopt: db %d" % (p, len(v)))
            out.append("    dw " + ",".join("%spv%d" % (p, i) for i in range(len(v))))
            for i, lines4 in enumerate(v):
                assert len(lines4) == 4
                out.append("%spv%d: dw %s" % (p, i, ",".join("%spv%d_%d" % (p, i, j) for j in range(4))))
                for j, line in enumerate(lines4):
                    check(line, 12, "popup")
                    out.append("%spv%d_%d:" % (p, i, j))
                    out.append(asm_str(fg(1) + bg(0) + line))
        elif f == "heads":
            for h in t[f]:
                assert len(h) == 20, h
            table_asm(p + "heads", t[f], out)
        else:
            table_asm(p + f, t[f], out, prefix=MISS_COLOUR if f in BAD_NEWS else "")
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")


def build(path):
    out = ["; generated by tools/texts.py - do not edit", ""]
    out.append("txt_hud_row0:")
    out.append(asm_str(HUD_ROW0))
    out.append("txt_hud_row1:")
    out.append(asm_str(HUD_ROW1))
    table_asm("msgs_clear", MSGS_CLEAR, out)
    for k, v in MSG.items():
        check(v, 40, k)
        out.append("%s:" % k)
        out.append(asm_str(v))
    # sanity: the patched positions
    assert MSG["msg_wave"].index("?") == 5 and MSG["msg_wave"][17:19] == "??"
    assert MSG["msg_streak"][14] == "?"
    out.append("txt_popup_ok:")
    out.append(asm_str(POPUP_OK))
    for c in CARDS:
        card_asm(c, out)

    out.append("diff_names: dw " + ",".join("dn_%d" % i for i in range(3)))
    for i, n in enumerate(DIFF_NAMES):
        out.append("dn_%d:" % i)
        out.append(asm_str(n))
    out.append("txt_select:")
    out.append(asm_str(TXT_SELECT))
    out.append("txt_hiscore:")
    out.append(asm_str(TXT_HISCORE))
    out.append("MENU_NPAGES equ %d" % len(MENU_PAGES))
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
    import os
    path = sys.argv[1] if len(sys.argv) > 1 else "build/texts.asm"
    build(path)
    for n in EP_TEXTS:
        build_episode(n, os.path.join(os.path.dirname(path), "ep%d_txt.asm" % n))
