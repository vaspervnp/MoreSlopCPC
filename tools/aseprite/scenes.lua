-- MORE SLOP: Blender scene renders -> CPC palettes, in Aseprite.
-- Each render is flattened on its background colour, the CPC palette is set
-- and the sprite converted to indexed colour with ordered (Bayer) dithering.
-- Line-art backgrounds are then "dimmed" with a checkerboard so that the
-- solid sprites always stand out. Shelf strips are drawn as pixel art.
local ROOT = "\\\\wsl.localhost\\Ubuntu\\home\\vasilhs\\repos\\MoreSlopCPC\\art\\"

local function C(h) return Color{ r=tonumber(h:sub(2,3),16), g=tonumber(h:sub(4,5),16), b=tonumber(h:sub(6,7),16), a=255 } end

local function convert(name, out, pal, dim, dither)
  local src = Image{ fromFile = ROOT .. "renders\\scenes\\" .. name .. ".png" }
  local spr = Sprite(src.width, src.height, ColorMode.RGB)
  local img = Image(src.width, src.height, ColorMode.RGB)
  local bg = C(pal[1])
  img:clear(app.pixelColor.rgba(bg.red, bg.green, bg.blue, 255))
  img:drawImage(src, Point(0, 0))
  -- force opaque
  for it in img:pixels() do
    local v = it()
    if app.pixelColor.rgbaA(v) < 255 then
      local a = app.pixelColor.rgbaA(v) / 255
      it(app.pixelColor.rgba(
        math.floor(app.pixelColor.rgbaR(v) * a + bg.red * (1 - a)),
        math.floor(app.pixelColor.rgbaG(v) * a + bg.green * (1 - a)),
        math.floor(app.pixelColor.rgbaB(v) * a + bg.blue * (1 - a)), 255))
    end
  end
  spr:newCel(spr.layers[1], 1, img, Point(0, 0))
  local P = Palette(#pal + 1)
  for i, h in ipairs(pal) do P:setColor(i - 1, C(h)) end
  P:setColor(#pal, C(pal[1]))   -- duplicate of pen 0: never wins a tie, keeps index #pal free
  spr:setPalette(P)
  app.activeSprite = spr
  app.activeLayer = spr.layers[1]
  app.command.BackgroundFromLayer()     -- opaque: no index is reserved for transparency
  spr.transparentColor = #pal           -- (out of range on purpose)
  app.command.ChangePixelFormat{ ui=false, format="indexed", dithering=dither and "ordered" or "none",
                                 ditheringMatrix="bayer4x4", ditheringFactor=1.0 }
  if dim then
    local cel = spr.layers[1]:cel(1)
    local im = cel.image
    for it in im:pixels() do
      if it() ~= 0 and ((it.x + it.y) % 2 == 1) then it(0) end
    end
  end
  spr:saveAs(ROOT .. "aseprite\\" .. out .. ".aseprite")
  spr:saveCopyAs(ROOT .. "png\\" .. out .. ".png")
  spr:close()
  print("ok " .. out)
end

local EP1 = { "#000080", "#00FFFF", "#FF00FF", "#FFFFFF" }
local EP2 = { "#000000", "#FF8000", "#800000", "#FFFF00" }
local EP3 = { "#000000", "#00FFFF", "#FF00FF", "#FFFFFF", "#000080", "#8000FF", "#800000", "#FF8000",
              "#FFFF00", "#FF8080", "#00FF00", "#008000", "#0080FF", "#808080", "#FF0000", "#FF0080" }
-- menu: everything but pens 1-3 (those belong to the rainbow logo)
local MENU13 = { "#000000", "#000080", "#0000FF", "#8000FF", "#FF00FF", "#FF0080", "#00FF00",
                 "#00FFFF", "#0080FF", "#FF8080", "#808080", "#FFFFFF", "#800000" }
local LOADER = { "#000000", "#000080", "#0000FF", "#8000FF", "#FF00FF", "#FF0080", "#FF0000", "#FF8000",
                 "#FFFF00", "#00FF00", "#00FFFF", "#0080FF", "#FF8080", "#808080", "#FFFFFF", "#800000" }

convert("bg1", "bg1_pf", EP1, true, false)
convert("bg2", "bg2_pf", EP2, true, false)
convert("bg3", "bg3_pf", EP3, false, true)
convert("menu_scene", "menu_scene", MENU13, false, true)
convert("loader_scene", "loader_scene", LOADER, false, true)

-- shelf strips: a store shelf with price tags -----------------------------
local function strip(out, w, rows, keys)
  local spr = Sprite(w, #rows, ColorMode.RGB)
  local img = Image(w, #rows, ColorMode.RGB)
  for y, row in ipairs(rows) do
    for x = 0, w - 1 do
      local k = row:sub((x % #row) + 1, (x % #row) + 1)
      local c = keys[k]
      img:drawPixel(x, y - 1, app.pixelColor.rgba(c.red, c.green, c.blue, 255))
    end
  end
  spr:newCel(spr.layers[1], 1, img, Point(0, 0))
  spr:saveAs(ROOT .. "aseprite\\" .. out .. ".aseprite")
  spr:saveCopyAs(ROOT .. "png\\" .. out .. ".png")
  spr:close()
  print("ok " .. out)
end

-- Mode 1 shelf (shelf palette: 0 = playfield pen 0, R dark red, O orange, Y yellow)
local S1 = { ["."]=C("#000080"), R=C("#800000"), O=C("#FF8000"), Y=C("#FFFF00") }
strip("shelf_m1", 320, {
  "................................................................",
  "................................................................",
  "YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY",
  "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO",
  "RRRRRRORRRRRRRRRRRRRRRRRORRRRRRRRRRRRRRRRROORRRRRRRRRRRRRRRRRRRR",
  "RRYYYYYYYYYRRRRRRRRRRRRRRRRRRRRRRRYYYYYYYYYRRRRRRRRRRRRRRRRRRRRR",
  "RRYRRORRORYRRRRRRRORRRRRRRRRRRRRRRYRORRORRYRRRRRRRRRRRRRRRRORRRR",
  "RRYYYYYYYYYRRRRRRRRRRRRRRRRRRRRRRRYYYYYYYYYRRRRRRRRRRRRRRRRRRRRR",
  "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO",
  "RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR" }, S1)
-- Mode 0 shelf for the graveyard: a mossy stone ledge (ep3 colours)
local S3 = { ["."]=C("#000000"), G=C("#008000"), L=C("#00FF00"), S=C("#808080"), D=C("#000080") }
strip("shelf_m0", 160, {
  "................................",
  "................................",
  "LGLLGLLLGLLGLLLLGLLGLLLGLLGLLLLG",
  "GSGSSSGSSSSGSSGSSSSGSSSGSSSSGSSS",
  "SSSSDSSSSSSSSDSSSSSSSDSSSSSSSSSS",
  "SSDSSSSSSSDSSSSSSSDSSSSSSSDSSSSS",
  "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD",
  "SSSSSSDSSSSSSSSSSSSDSSSSSSSSSSSS",
  "SSSDSSSSSSSSSDSSSSSSSSSSSDSSSSSS",
  "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD" }, S3)

-- logos: kept in full colour with alpha; build_assets maps brightness onto
-- the cycling rainbow pens (menu) or the fire colours (loader)
local function logo(name)
  local spr = Sprite{ fromFile = ROOT .. "renders\\scenes\\" .. name .. ".png" }
  spr:saveAs(ROOT .. "aseprite\\" .. name .. ".aseprite")
  spr:saveCopyAs(ROOT .. "png\\" .. name .. ".png")
  spr:close()
  print("ok " .. name)
end
logo("menu_logo")
logo("loader_logo")
