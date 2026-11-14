"""Record a 4-minute tour of MORE SLOP from the headless emulator.

    python3 tests/video.py          -> build/video/moreslop.mp4 (1080p, 25 fps)
    python3 tests/video.py --dry    -> just print the timeline

The tour: power on, the loading screen, the menu (with the episode pages),
then the first wave of each of the ten episodes, and the fight against the
SlopBot at the end of episode 10 followed by the victory card (held so the
whole thing lasts 4:00). The autopilot catches the power-ups. Waves 2-3 are
played off camera (fast, with the quota cut short); every cut fades.

The run is deterministic (fixed autopilot seed, emulated machine), so the
dry run predicts the real one exactly. Pictures are taken every second 50 Hz
frame (the game runs at 25 fps); the AY registers are logged every frame and
synthesized into the soundtrack.
"""
import os
import struct
import subprocess
import sys
import wave

sys.path.insert(0, os.path.dirname(__file__))
from harness import Game, BUILD, KEY_SPACE  # noqa: E402
from autopilot import Autopilot  # noqa: E402
import record_music as RM  # noqa: E402

OUT = os.path.join(BUILD, "video")
W, H = 768, 544
KEY_ENTER = 0x0D
FADE = 12                   # frames (50 Hz) of each fade


class Recorder:
    def __init__(self, g, dry):
        self.g, self.dry = g, dry
        self.n = 0                       # recorded 50 Hz frames
        self.regs = []
        self.gain = []
        self.fade_in = 0
        self.proc = None
        if not dry:
            os.makedirs(OUT, exist_ok=True)
            self.raw = os.path.join(OUT, "raw.mkv")
            self.proc = subprocess.Popen(
                ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                 "-s", "%dx%d" % (W, H), "-r", "25", "-i", "-",
                 "-c:v", "libx264", "-preset", "veryfast", "-qp", "0", self.raw],
                stdin=subprocess.PIPE)

    def t(self):
        return self.n / 50.0

    def mark(self, what):
        print("%6.1fs  %s" % (self.t(), what), flush=True)

    def _frame(self, level):
        c = self.g.c
        c.run_frames(1)
        self.regs.append(c.psg_regs())
        self.gain.append(level)
        if self.proc and self.n % 2 == 0:
            img = c.image(aspect=True)
            if level < 1.0:
                img = img.point(lambda v: int(v * level))
            self.proc.stdin.write(img.tobytes())
        self.n += 1

    def frames(self, count, each=None):
        for _ in range(count):
            if each and self.n % 2 == 0:
                each()
            level = 1.0
            if self.fade_in:
                level = 1.0 - self.fade_in / FADE
                self.fade_in -= 1
            self._frame(level)

    def cut(self, each=None):
        """Fade out (the game keeps running); the next frames fade in."""
        for i in range(FADE):
            if each and self.n % 2 == 0:
                each()
            self._frame(1.0 - (i + 1) / FADE)
        self.fade_in = FADE

    def tap(self, key, hold=4, gap=6):
        self.g.c.key_down(key)
        self.frames(hold)
        self.g.c.key_up(key)
        self.frames(gap)

    def close(self):
        if self.proc:
            self.proc.stdin.close()
            self.proc.wait()


def render_audio(regs, gains, path):
    """record_music.render with a volume envelope (for the fades)."""
    rate = RM.RATE
    spf = rate // 50
    phase = [0.0, 0.0, 0.0]
    lfsr, nphase, nout = 1, 0.0, 1
    out = bytearray()
    for r, gain in zip(regs, gains):
        per = [(r[0] | (r[1] & 15) << 8) or 1, (r[2] | (r[3] & 15) << 8) or 1, (r[4] | (r[5] & 15) << 8) or 1]
        np_ = (r[6] & 31) or 1
        mix = r[7]
        vols = [RM.VOL[r[8] & 15], RM.VOL[r[9] & 15], RM.VOL[r[10] & 15]]
        for _ in range(spf):
            s = 0.0
            nphase += RM.AY_CLOCK / 16.0 / np_ / rate
            while nphase >= 1.0:
                nphase -= 1.0
                bit = (lfsr ^ (lfsr >> 3)) & 1
                lfsr = (lfsr >> 1) | (bit << 16)
                nout = lfsr & 1
            for ch in range(3):
                phase[ch] += RM.AY_CLOCK / 16.0 / per[ch] / rate
                phase[ch] %= 1.0
                t = (phase[ch] < 0.5) if not (mix >> ch) & 1 else True
                n = nout if not (mix >> (ch + 3)) & 1 else True
                if t and n:
                    s += vols[ch]
            out += struct.pack("<h", int((s / 3.0 - 0.25) * 30000 * gain))
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(bytes(out))


def main():
    dry = "--dry" in sys.argv
    play_s = float(next((a[7:] for a in sys.argv if a.startswith("--play=")), "15.4"))
    seed = int(next((a[7:] for a in sys.argv if a.startswith("--seed=")), "6"))
    g = Game(boot=False)
    c = g.c
    r = Recorder(g, dry)
    ap = Autopilot(g, seed=seed, skill=0.92)

    def st():
        return g.b("state")

    def offscreen(until, limit=50 * 240):
        """Play on, unrecorded, until until() is true. Waves end quickly."""
        for _ in range(limit // 2):
            if until():
                return True
            if st() == 1 and not g.b("boss_on") and g.b("quota_left") > 1:
                g.poke("quota_left", 1)
            g.poke("misses", 0)
            if g.b("lives") < 2:
                g.poke("lives", 3)
            if st() == 0:
                c.key_down(KEY_SPACE)
                c.run_frames(2)
                c.key_up(KEY_SPACE)
                c.run_frames(2)
                continue
            ap.step()
            c.run_frames(2)
        return False

    # --- power on, type RUN"LOADER, the loading screen
    c.run_frames(40)
    r.mark("boot")
    r.frames(80)
    c.insert_disc(os.path.join(BUILD, "moreslop.dsk"))
    for ch in 'RUN"LOADER\n':
        r.tap(KEY_ENTER if ch == "\n" else ch, 4, 5)
    r.frames(320)                       # (a multiple of 10: keeps the rest in step)
    r.cut()
    while g.w("raster_ptr") != g.sym["rast_menu"]:
        c.run_frames(10)
    c.run_frames(10)

    # --- the menu: logo, the tour pages, start
    r.mark("menu")
    r.frames(110)
    for _ in range(5):                  # off camera: on to "the tour, part 1"
        c.key_down(ord("H"))
        c.run_frames(4)
        c.key_up(ord("H"))
        c.run_frames(6)
    r.fade_in = 0
    r.frames(120)
    r.tap(ord("H"))
    r.frames(120)
    r.tap(KEY_SPACE)

    # --- one wave of each episode
    for ep in range(10):
        if ep:
            ok = offscreen(lambda: st() == 0 and g.b("episode") == ep and g.b("wave") == 0)
            assert ok, "never reached episode %d" % (ep + 1)
            r.fade_in = FADE
        while st() != 0:
            r.frames(2)
        r.mark("episode %d card" % (ep + 1))
        r.frames(130)
        r.tap(KEY_SPACE)
        r.mark("episode %d play" % (ep + 1))
        t0 = r.t()
        card_at = None
        shown = g.b("pw_show")
        while r.t() - t0 < play_s and st() != 4:
            if g.b("pw_show") != shown:
                shown = g.b("pw_show")
                if shown:
                    r.mark("  caught power-up %d" % shown)
            if st() == 0 and g.b("episode") == ep:       # the next wave's card
                card_at = card_at or r.t()
                if r.t() - card_at > 1.2:
                    r.tap(KEY_SPACE)
                    card_at = None
                    continue
            r.frames(2, ap.step)
        r.mark("  end of segment: state %d wave %d lives %d quota %d" % (st(), g.b("wave"), g.b("lives"),
                                                                       g.b("quota_left")))
        r.cut(ap.step)
        ap.release()

    # --- episode 10, wave 3: the boss
    ok = offscreen(lambda: st() == 1 and g.b("wave") == 2)
    assert ok, "never reached the last wave"
    g.poke("quota_left", 3)
    r.fade_in = FADE
    r.mark("episode 10 wave 3")
    for _ in range(50 * 90 // 2):
        if st() == 5:
            break
        g.poke("misses", 0)
        r.frames(2, ap.step)
    ap.release()
    r.mark("victory (state %d)" % st())
    r.frames(max(250, 50 * 240 - FADE - r.n))     # hold the card to exactly 4:00
    r.cut()
    r.mark("end")
    r.close()
    if dry:
        return

    wav = os.path.join(OUT, "sound.wav")
    render_audio(r.regs, r.gain, wav)
    out = os.path.join(OUT, "moreslop.mp4")
    vf = "scale=1524:1080:flags=lanczos,pad=1920:1080:(ow-iw)/2:0"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", r.raw, "-i", wav,
                    "-vf", vf, "-c:v", "libx264", "-preset", "slow", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", out], check=True)
    print(out, "%.1f s" % r.t())


if __name__ == "__main__":
    main()
