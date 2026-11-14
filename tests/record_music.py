"""Record the AY registers from the emulated CPC and render them to WAV.

    python3 tests/record_music.py      -> build/music/*.wav

The emulator has no audio output, so this logs the 14 AY registers once
per 50 Hz frame and synthesizes them (square-wave tones, LFSR noise, the
AY's logarithmic volume table) - close enough to judge the tunes.
"""
import os
import struct
import sys
import wave

sys.path.insert(0, os.path.dirname(__file__))
from harness import Game, BUILD, KEY_SPACE  # noqa: E402

RATE = 22050
AY_CLOCK = 1000000
VOL = [0, 0.0105, 0.0154, 0.0216, 0.0319, 0.0461, 0.0638, 0.1071,
       0.1302, 0.2108, 0.2944, 0.3794, 0.4924, 0.6385, 0.8156, 1.0]


def record(g, frames):
    regs = []
    for _ in range(frames):
        g.c.run_frames(1)
        regs.append(g.c.psg_regs())
    return regs


def render(regs, path):
    spf = RATE // 50
    phase = [0.0, 0.0, 0.0]
    lfsr, nphase, nout = 1, 0.0, 1
    out = bytearray()
    for r in regs:
        per = [(r[0] | (r[1] & 15) << 8) or 1, (r[2] | (r[3] & 15) << 8) or 1, (r[4] | (r[5] & 15) << 8) or 1]
        np_ = (r[6] & 31) or 1
        mix = r[7]
        vols = [VOL[r[8] & 15], VOL[r[9] & 15], VOL[r[10] & 15]]
        for _ in range(spf):
            s = 0.0
            nphase += AY_CLOCK / 16.0 / np_ / RATE
            while nphase >= 1.0:
                nphase -= 1.0
                bit = (lfsr ^ (lfsr >> 3)) & 1
                lfsr = (lfsr >> 1) | (bit << 16)
                nout = lfsr & 1
            for ch in range(3):
                phase[ch] += AY_CLOCK / 16.0 / per[ch] / RATE
                phase[ch] %= 1.0
                tone_on = not (mix >> ch) & 1
                noise_on = not (mix >> (ch + 3)) & 1
                t = (phase[ch] < 0.5) if tone_on else True
                n = nout if noise_on else True
                if t and n:
                    s += vols[ch]
            out += struct.pack("<h", int((s / 3.0 - 0.25) * 30000))
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(bytes(out))
    return path


def main():
    os.makedirs(os.path.join(BUILD, "music"), exist_ok=True)
    g = Game()
    regs = record(g, 50 * 32)
    print(render(regs, os.path.join(BUILD, "music", "menu.wav")))
    notes = len(set((r[0], r[1]) for r in regs))
    print("menu: %d distinct lead periods, max volume %d" % (notes, max(r[8] for r in regs)))
    for ep in range(3):
        g = Game()
        g.poke("start_ep", ep)
        g.tap(KEY_SPACE)
        g.run(20)
        regs = record(g, 50 * 24)
        print(render(regs, os.path.join(BUILD, "music", "episode%d.wav" % (ep + 1))))


if __name__ == "__main__":
    main()
