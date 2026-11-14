# MORE SLOP - Amstrad CPC 6128
ASM  = rasm
DSK  = build/moreslop.dsk
PY   = python3

EPS    = 1 2 3 4 5 6 7 8 9 10
ASSETS = build/tables.asm build/palettes.asm build/sprites.asm \
         $(EPS:%=build/BG%) build/MENU.SCR build/SLOPSCR build/loader.bas
GEN    = build/music_data.asm build/texts.asm build/episodes.asm
SRC    = $(wildcard src/*.asm)
ART    = $(wildcard art/png/*.png)

all: $(DSK)

build/music_data.asm: tools/music.py
	@mkdir -p build
	$(PY) tools/music.py $@

build/texts.asm: tools/texts.py tools/episodes.py
	@mkdir -p build
	$(PY) tools/texts.py $@

build/episodes.asm: tools/episodes.py
	@mkdir -p build
	$(PY) tools/episodes.py $@

$(ASSETS) &: tools/build_assets.py tools/cpcgfx.py tools/placeholders.py tools/episodes.py $(ART)
	@mkdir -p build
	$(PY) tools/build_assets.py

build/LOW.BIN build/HIGH.BIN &: $(SRC) $(ASSETS) $(GEN)
	$(ASM) src/main.asm -o build/moreslop -s -sl -sv -sq -eo > build/rasm.log 2>&1 || (cat build/rasm.log; exit 1)
	@grep -E "LOW|HIGH" build/rasm.log

build/BANK5 build/BANK6 build/BANK7 &: build/LOW.BIN build/HIGH.BIN $(ASSETS) tools/pack_banks.py
	$(PY) tools/pack_banks.py

$(DSK): build/LOW.BIN build/HIGH.BIN build/BANK5 build/BANK6 build/BANK7 $(ASSETS)
	rm -f $(DSK)
	iDSK $(DSK) -n > /dev/null
	iDSK $(DSK) -i build/loader.bas -t 0 -f > /dev/null
	cd build && iDSK moreslop.dsk -i SLOPSCR -t 1 -c C000 -e C000 -f > /dev/null
	cd build && iDSK moreslop.dsk -i BANK5 -t 1 -c 4000 -e 4000 -f > /dev/null
	cd build && iDSK moreslop.dsk -i BANK6 -t 1 -c 4000 -e 4000 -f > /dev/null
	cd build && iDSK moreslop.dsk -i BANK7 -t 1 -c 4000 -e 4000 -f > /dev/null
	cd build && iDSK moreslop.dsk -i HIGH.BIN -t 1 -c 4000 -e 4000 -f > /dev/null
	cd build && iDSK moreslop.dsk -i LOW.BIN -t 1 -c 0040 -e 0040 -f > /dev/null
	iDSK $(DSK) -l
	@echo 'Ready: $(DSK)   ->   RUN"LOADER'

clean:
	rm -rf build

.PHONY: all clean
