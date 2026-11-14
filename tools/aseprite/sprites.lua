-- MORE SLOP: turn Blender renders into CPC-ready sprite sheets.
-- Run inside Aseprite (batch). JOBS is prepended by tools/aseprite_jobs.py.
--
-- For every job:  one animation frame per render, every pixel snapped to the
-- episode palette (alpha < 50% = transparent), a 1-pixel outline in pen 0,
-- saved as art/aseprite/<name>.aseprite and exported as a horizontal sheet
-- art/png/<name>.png (what tools/build_assets.py reads).

local function hexcol(h)
  return Color{ r=tonumber(h:sub(2,3),16), g=tonumber(h:sub(4,5),16), b=tonumber(h:sub(6,7),16), a=255 }
end

local function nearest(pal, r, g, b)
  local best, bd = 1, 1e9
  for i, c in ipairs(pal) do
    local d = (r-c.red)^2 + (g-c.green)^2 + (b-c.blue)^2
    if d < bd then best, bd = i, d end
  end
  return pal[best]
end

local function process(job)
  local pal = {}
  for i, h in ipairs(job.palette) do pal[i] = hexcol(h) end
  local spr = Sprite(job.w, job.h, ColorMode.RGB)
  local P = Palette(#pal + 1)
  P:setColor(0, Color{ r=0, g=0, b=0, a=0 })
  for i, c in ipairs(pal) do P:setColor(i, c) end
  spr:setPalette(P)
  local layer = spr.layers[1]
  layer.name = job.name
  for f, path in ipairs(job.frames) do
    if f > 1 then spr:newEmptyFrame() end
    local src = Image{ fromFile = path }
    local img = Image(job.w, job.h, ColorMode.RGB)
    -- snap to the palette
    for y = 0, job.h - 1 do
      for x = 0, job.w - 1 do
        local px = 0
        -- the render may be wider than the sprite: sample the nearest column
        local sx = math.floor((x + 0.5) * src.width / job.w)
        if sx < src.width and y < src.height then px = src:getPixel(sx, y) end
        local a = app.pixelColor.rgbaA(px)
        if a >= 128 then
          local c = nearest(pal, app.pixelColor.rgbaR(px), app.pixelColor.rgbaG(px), app.pixelColor.rgbaB(px))
          img:drawPixel(x, y, app.pixelColor.rgba(c.red, c.green, c.blue, 255))
        else
          img:drawPixel(x, y, 0)
        end
      end
    end
    -- outline: transparent pixels next to opaque ones become pen 0
    if job.outline then
      local o = pal[1]
      local ov = app.pixelColor.rgba(o.red, o.green, o.blue, 255)
      local copy = img:clone()
      for y = 0, job.h - 1 do
        for x = 0, job.w - 1 do
          if app.pixelColor.rgbaA(copy:getPixel(x, y)) == 0 then
            local hit = false
            for _, d in ipairs({{1,0},{-1,0},{0,1},{0,-1}}) do
              local nx, ny = x + d[1], y + d[2]
              if nx >= 0 and ny >= 0 and nx < job.w and ny < job.h then
                local q = copy:getPixel(nx, ny)
                if app.pixelColor.rgbaA(q) > 0 and q ~= ov then hit = true end
              end
            end
            if hit then img:drawPixel(x, y, ov) end
          end
        end
      end
    end
    spr:newCel(layer, f, img, Point(0, 0))
    spr.frames[f].duration = job.ms or 160
  end
  spr:saveAs(job.aseprite)
  -- horizontal sheet
  local sheet = Image(job.w * #job.frames, job.h, ColorMode.RGB)
  for f = 1, #job.frames do
    local cel = layer:cel(f)
    if cel then sheet:drawImage(cel.image, Point((f - 1) * job.w + cel.position.x, cel.position.y)) end
  end
  sheet:saveAs(job.png)
  spr:close()
  print("ok " .. job.name .. " " .. #job.frames .. " frames")
end

for _, job in ipairs(JOBS) do
  local ok, err = pcall(process, job)
  if not ok then print("FAIL " .. job.name .. ": " .. tostring(err)) end
end
