"""Pack the menu, the ten backgrounds and the episode blobs into banks #C5-#C7.

    python3 tools/pack_banks.py      (after rasm has written build/EP<n>HI/LO.BIN)

Bank #C4 is left free: it holds the unpacked background of the current
episode. The directory sits at the start of bank #C5 (seen at #4000):
    entry k: db bank config, dw address       (3 bytes)
    k = 0 menu picture, then per episode n (1..10):
        3n-2 background, 3n-1 HIGH blob, 3n LOW blob
Each packed stream is LZ2 (tools/cpcgfx.py, src/video.asm lz2_unpack) and
never crosses a bank.
"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cpcgfx as G      # noqa: E402
import episodes as E    # noqa: E402

BUILD = os.path.join(os.path.dirname(HERE), "build")
CACHE = os.path.join(BUILD, "lzcache")
BANKS = [0xC5, 0xC6, 0xC7]


def _pack(path):
    with open(path, "rb") as f:
        return G.lz2_pack(f.read(), CACHE)


def main():
    files = [os.path.join(BUILD, "MENU.SCR")]
    for e in E.EPISODES:
        n = e["n"]
        files += [os.path.join(BUILD, "BG%d" % n), os.path.join(BUILD, "EP%dHI.BIN" % n),
                  os.path.join(BUILD, "EP%dLO.BIN" % n)]
    with ProcessPoolExecutor() as ex:
        packed = list(ex.map(_pack, files))
    ndir = 3 * len(files)
    banks = [bytearray(ndir), bytearray(), bytearray()]
    where = []
    # first fit, largest first, so the small blobs fill the gaps
    order = sorted(range(len(files)), key=lambda i: -len(packed[i]))
    place = [None] * len(files)
    for i in order:
        for b in range(3):
            if len(banks[b]) + len(packed[i]) <= 0x4000:
                place[i] = (b, len(banks[b]))
                banks[b] += packed[i]
                break
        else:
            sys.exit("out of bank space: %s (%d bytes)" % (files[i], len(packed[i])))
    for i, (b, off) in enumerate(place):
        addr = 0x4000 + off
        banks[0][3 * i:3 * i + 3] = bytes([BANKS[b], addr & 255, addr >> 8])
        where.append((os.path.basename(files[i]), len(packed[i]), BANKS[b], addr))
    for b in range(3):
        with open(os.path.join(BUILD, "BANK%d" % (5 + b)), "wb") as f:
            f.write(banks[b] or b"\0")      # BASIC wants a non-empty file
    raw = sum(os.path.getsize(f) for f in files)
    pk = sum(len(p) for p in packed)
    print("banks: %d -> %d bytes packed; free %s" % (raw, pk, ", ".join(
        "#%02X %d" % (BANKS[b], 0x4000 - len(banks[b])) for b in range(3))))
    with open(os.path.join(BUILD, "banks.txt"), "w") as f:
        for name, size, cfg, addr in where:
            f.write("%-12s %5d  #%02X:%04X\n" % (name, size, cfg, addr))


if __name__ == "__main__":
    main()
