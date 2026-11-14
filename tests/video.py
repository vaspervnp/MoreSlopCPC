"""Record a gameplay video of MORE SLOP from the headless emulator.

    python3 tests/video.py          -> build/video/moreslop.mp4 (1080p, 25 fps)
    python3 tests/video.py --dry    -> just print the timeline

The run is fully deterministic (fixed autopilot seed, emulated machine), so
the dry run predicts the real one exactly. Pictures are taken every second
50 Hz frame (the game runs at 25 fps); the AY registers are logged every
frame and synthesized into the soundtrack (tests/record_music.py).
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from harness import Game, BUILD, KEY_SPACE, KEY_DOWN  # noqa: E402
from autopilot import Autopilot  # noqa: E402
import record_music  # noqa: E402

OUT = os.path.join(BUILD, "video")
W, H = 768, 544
KEY_ENTER = 0x0D


class Recorder:
    def __init__(self, g, dry):
        self.g, self.dry = g, dry
        self.n = 0                       # recorded 50 Hz frames
        self.regs = []
        self.marks = []
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
        self.marks.append((self.t(), what))
        print("%6.1fs  %s" % (self.t(), what), flush=True)

    def frames(self, count, each=None):
        c = self.g.c
        for _ in range(count):
            if each and self.n % 2 == 0:
                each()
            c.run_frames(1)
            self.regs.append(c.psg_regs())
            if self.proc and self.n % 2 == 0:
                self.proc.stdin.write(c.image(aspect=True).tobytes())
            self.n += 1

    def tap(self, key, hold=4, gap=6):
        self.g.c.key_down(key)
        self.frames(hold)
        self.g.c.key_up(key)
        self.frames(gap)

    def skip(self, count):
        self.g.c.run_frames(count)

    def close(self):
        if self.proc:
            self.proc.stdin.close()
            self.proc.wait()


def main():
    dry = "--dry" in sys.argv
    seed = int(next((a[7:] for a in sys.argv if a.startswith("--seed=")), "6"))
    g = Game(boot=False)
    c = g.c
    r = Recorder(g, dry)

    # --- power on, type RUN"LOADER, watch the loading screen arrive
    r.skip(40)
    r.mark("boot screen")
    r.frames(90)
    c.insert_disc(os.path.join(BUILD, "moreslop.dsk"))
    for ch in 'RUN"LOADER\n':
        r.tap(KEY_ENTER if ch == "\n" else ch, 4, 5)
    r.mark("loading")
    r.frames(230)
    # the static part of the load is cut out
    while True:
        r.skip(10)
        if g.w("raster_ptr") == g.sym["rast_menu"]:
            break
    r.mark("menu")

    # --- menu: rainbow logo, an info page, the difficulty list
    r.frames(130)
    r.tap(ord("H"))
    r.frames(120)
    r.tap(KEY_DOWN, 4, 25)
    r.tap(0x0B, 4, 30)                    # back up to TERMINALLY ONLINE
    r.mark("start")
    r.tap(KEY_SPACE)

    # --- play until the victory card (or the end of the lives)
    ap = Autopilot(g, seed=seed, skill=0.9)
    last = None
    win_at = None
    while r.t() < 300:
        st = (g.b("state"), g.b("episode"), g.b("wave"))
        if st != last:
            r.mark("state %d  ep %d  wave %d  lives %d  score %s"
                   % (st[0], st[1] + 1, st[2] + 1, g.b("lives"), c.read_ram(g.sym["score"], 3).hex()))
            last = st
            if st[0] == 0:                 # wave / episode card: time to read it
                r.frames(150 if st[2] == 0 else 60)
                r.tap(KEY_SPACE)
                continue
            if st[0] == 5 and win_at is None:
                win_at = r.t()
            if st[0] == 4:
                r.frames(250)
                break
        if win_at is not None and r.t() - win_at > 6:
            break
        r.frames(2, ap.step)
    ap.release()
    r.mark("end")
    r.close()
    if dry:
        return

    wav = os.path.join(OUT, "sound.wav")
    record_music.render(r.regs, wav)
    total = r.t()
    out = os.path.join(OUT, "moreslop.mp4")
    vf = ("scale=1524:1080:flags=lanczos,pad=1920:1080:(ow-iw)/2:0,"
          "fade=t=in:st=0:d=0.6,fade=t=out:st=%.2f:d=2" % (total - 2))
    af = "afade=t=in:st=0:d=0.3,afade=t=out:st=%.2f:d=2" % (total - 2)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", r.raw, "-i", wav,
                    "-vf", vf, "-af", af, "-c:v", "libx264", "-preset", "slow", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", out], check=True)
    print(out, "%.1f s" % total)


if __name__ == "__main__":
    main()
