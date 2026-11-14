"""Write the Lua job list for tools/aseprite/sprites.lua.

    python3 tools/aseprite_jobs.py > build/aseprite_run.lua
The output is the full script to run inside Aseprite (via the Aseprite MCP).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cpcgfx as G  # noqa: E402

WIN = r"\\wsl.localhost\Ubuntu\home\vasilhs\repos\MoreSlopCPC"

THEMIS = ["idle", "walk1", "walk2", "zap", "dizzy"]
# name, render dir, frame files, palette, (w, h)
JOBS = [
    ("themis_m1", "themis_m1", THEMIS, "ep1", 24, 24),
    ("themis_m0", "themis_m0", THEMIS, "ep3", 12, 24),
    ("robot_m1", "robot_m1", ["0", "1"], "ep1", 32, 20),
    ("robot_m0", "robot_m0", ["0", "1"], "ep3", 16, 20),
    ("items_ep1", "items_ep1", ["0_0", "0_1", "1_0", "1_1", "2_0", "2_1"], "ep1", 16, 16),
    ("items_ep2", "items_ep2", ["0_0", "0_1", "1_0", "1_1", "2_0", "2_1"], "ep2", 16, 16),
    ("items_ep3", "items_ep3", ["0_0", "0_1", "1_0", "1_1", "2_0", "2_1"], "ep3", 8, 16),
    ("power_m1", "power_m1", ["0", "1"], "ep1", 16, 16),
    ("power_m0", "power_m0", ["0", "1"], "ep3", 8, 16),
    ("bro_walk", "bro_walk", ["0", "1"], "ep3", 12, 24),
    ("bro_float", "bro_float", ["0"], "ep3", 12, 32),
]


def lua_str(s):
    return '"' + s.replace("\\", "\\\\") + '"'


def main():
    out = ["JOBS = {"]
    for name, d, frames, pal, w, h in JOBS:
        cols = [G.hexrgb(f) for f in G.PAL[pal]]
        fr = [lua_str(WIN + "\\art\\renders\\%s\\%s.png" % (d, f)) for f in frames]
        out.append("  { name=%s, w=%d, h=%d, outline=true, palette={%s}, frames={%s}, aseprite=%s, png=%s },"
                   % (lua_str(name), w, h, ",".join(lua_str(c) for c in cols), ",".join(fr),
                      lua_str(WIN + "\\art\\aseprite\\%s.aseprite" % name),
                      lua_str(WIN + "\\art\\png\\%s.png" % name)))
    out.append("}")
    with open(os.path.join(HERE, "aseprite", "sprites.lua")) as f:
        out.append(f.read())
    sys.stdout.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
