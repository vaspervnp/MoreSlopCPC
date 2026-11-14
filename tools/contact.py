"""Contact sheet of the Blender renders (for review)."""
import os, sys
from PIL import Image
R = "art/renders"
out = sys.argv[1]
rows = []
for d in sorted(os.listdir(R)):
    fs = sorted(f for f in os.listdir(os.path.join(R, d)) if f.endswith(".png"))
    ims = []
    for f in fs:
        im = Image.open(os.path.join(R, d, f)).convert("RGBA")
        if d.endswith("m0") or d.startswith(("items_ep3", "bro")) or d == "power_m0":
            im = im.resize((im.width * 2, im.height), Image.NEAREST)
        ims.append(im)
    rows.append(ims)
W = max(sum(i.width + 2 for i in r) for r in rows)
H = sum(max(i.height for i in r) + 2 for r in rows)
sheet = Image.new("RGBA", (W, H), (50, 50, 50, 255))
y = 0
for r in rows:
    x = 0
    for im in r:
        sheet.paste(im, (x, y), im)
        x += im.width + 2
    y += max(i.height for i in r) + 2
sheet.resize((W * 5, H * 5), Image.NEAREST).save(out)
