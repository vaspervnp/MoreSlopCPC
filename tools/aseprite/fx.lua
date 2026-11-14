-- MORE SLOP: hand-drawn effects (poofs and zap bolts), drawn in Aseprite.
-- Each frame is a pixel map: one character per pixel, '.' transparent.
local ROOT = "\\\\wsl.localhost\\Ubuntu\\home\\vasilhs\\repos\\MoreSlopCPC\\art\\"

local function C(h) return { tonumber(h:sub(2,3),16), tonumber(h:sub(4,5),16), tonumber(h:sub(6,7),16) } end

local function make(name, w, h, keys, frames)
  local spr = Sprite(w, h, ColorMode.RGB)
  local layer = spr.layers[1]
  layer.name = name
  for f, rows in ipairs(frames) do
    if f > 1 then spr:newEmptyFrame() end
    local img = Image(w, h, ColorMode.RGB)
    for y, row in ipairs(rows) do
      for x = 1, #row do
        local k = row:sub(x, x)
        local c = keys[k]
        if c then img:drawPixel(x - 1, y - 1, app.pixelColor.rgba(c[1], c[2], c[3], 255)) end
      end
    end
    spr:newCel(layer, f, img, Point(0, 0))
    spr.frames[f].duration = 120
  end
  spr:saveAs(ROOT .. "aseprite\\" .. name .. ".aseprite")
  local sheet = Image(w * #frames, h, ColorMode.RGB)
  for f = 1, #frames do sheet:drawImage(layer:cel(f).image, Point((f - 1) * w, 0)) end
  sheet:saveAs(ROOT .. "png\\" .. name .. ".png")
  spr:close()
  print("ok " .. name)
end

-- episode 1 / 2 (Mode 1): W white, C cyan, M magenta, B dark blue
local M1 = { W=C("#FFFFFF"), C=C("#00FFFF"), M=C("#FF00FF"), B=C("#000080") }
make("poof_m1", 16, 16, M1, {
  { "................",
    ".......M........",
    "...M...M...M....",
    "....M..W..M.....",
    ".....MWWWM......",
    "......WWW.......",
    "..MMWWWWWWWMM...",
    "......WWW.......",
    ".....MWWWM......",
    "....M..W..M.....",
    "...M...M...M....",
    ".......M........",
    "................",
    "................",
    "................",
    "................" },
  { "......C..C......",
    "...C..........C.",
    ".....CCCCCC.....",
    "....CC....CC....",
    "...CC..WW..CC...",
    "C..C..W..W..C...",
    "...C.W....W.C..C",
    "...C.W....W.C...",
    "...C..W..W..C...",
    "...CC..WW..CC...",
    "C...CC....CC....",
    ".....CCCCCC...C.",
    "..C.............",
    ".......C...C....",
    "................",
    "................" },
  { "..M...........C.",
    "........C.......",
    "C...............",
    ".....M......M...",
    "..............C.",
    ".C..............",
    "..........W.....",
    "....W...........",
    "...............M",
    "..M.....C.......",
    "............C...",
    "......M.........",
    "C...........W...",
    "....C...........",
    "..........M.....",
    "................" },
})

make("bolt_m1", 8, 10, M1, {
  { "...WWC..",
    "..WWC...",
    ".WWC....",
    "WWWWWWC.",
    "...WWC..",
    "..WWC...",
    ".WWC....",
    "WWWWWWC.",
    "...WC...",
    "..WC...." },
})

-- episode 3 (Mode 0, 2:1 pixels): Y yellow, O orange, R bright red, W white
local M0 = { Y=C("#FFFF00"), O=C("#FF8000"), R=C("#FF0000"), W=C("#FFFFFF") }
make("poof_m0", 8, 16, M0, {
  { "........",
    "...R....",
    ".R.O.R..",
    "..OYO...",
    "ROYWYOR.",
    "..OYO...",
    ".R.O.R..",
    "...R....",
    "........",
    "........",
    "........",
    "........",
    "........",
    "........",
    "........",
    "........" },
  { "..O..O..",
    "...OO...",
    ".OOYYOO.",
    ".OY..YO.",
    "ROY.WYOR",
    ".OY..YO.",
    ".OOYYOO.",
    "...OO...",
    ".R....R.",
    "....R...",
    "........",
    "........",
    "........",
    "........",
    "........",
    "........" },
  { ".R....O.",
    "....Y...",
    "O.......",
    "...R..R.",
    ".......Y",
    "Y.......",
    "....O...",
    "..O.....",
    ".......R",
    "R...Y...",
    "......O.",
    "...R....",
    "O......Y",
    "..Y.....",
    "........",
    "........" },
})

make("bolt_m0", 4, 10, M0, {
  { "..WY",
    ".WY.",
    "WY..",
    "WWWY",
    ".WY.",
    "WY..",
    "WWWY",
    ".WY.",
    "WY..",
    "Y..." },
})
