; ============================================================================
;  MORE SLOP  -  an Amstrad CPC 6128 arcade game
;
;  Memory map once the game runs (firmware is gone):
;    #0000-#003F  restarts; #0038 jumps to int_handler
;    #0040-#3EFF  LOW: code, music, tables, variables   (loaded by `entry`)
;    #3F00-#3FFF  stack
;    #4000-#7FFF  HIGH: font, sprites, texts  /  window for banks #C4-#C7
;    #8000-#BFFF  screen buffer B
;    #C000-#FFFF  screen buffer A
;  Banks: #C4 background of the current episode; #C5-#C7 everything else,
;  packed (menu picture, the ten backgrounds, the episode blobs).
;  #6800-#7FFF holds the current episode's HIGH blob, lo_slot its LOW blob.
; ============================================================================

    include "const.asm"
    include "../build/ep_const.asm"

; ============================================================================
; LOW
; ============================================================================
    org #0040
low_start:

low_init:
    di
    ld sp,STACK_TOP
    im 1
    ld a,#C3
    ld (#0038),a
    ld hl,int_handler
    ld (#0039),hl
    ld bc,#7F00+GA_MODE0
    out (c),c
    ld bc,#7F10             ; border
    out (c),c
    ld c,#54
    out (c),c
    ld a,CFG_BASE
    call set_cfg
    ld hl,rast_none
    ld (raster_ptr),hl
    xor a
    ld (vbl_count),a
    ei
    jp menu

    include "int.asm"
    include "music.asm"
    include "video.asm"
    include "overlay.asm"
    include "hud.asm"
    include "game.asm"
    include "obstacles.asm"
    include "menu.asm"
    include "episode.asm"
    include "data.asm"
    include "../build/tables.asm"
    include "../build/palettes.asm"
    include "../build/music_data.asm"
    include "vars.asm"
low_end:

    assert low_end <= #3F00
    print "LOW  #0040-",{hex4}low_end," free ",#3F00-low_end
    save "build/LOW.BIN",#0040,low_end-#0040

; ============================================================================
; HIGH - loaded by BASIC at #4000; `entry` runs while the firmware is alive
; ============================================================================
    org #4000
high_start:

entry:
    ld b,low_name_end-low_name
    ld hl,low_name
    ld de,#8000             ; 2K buffer for AMSDOS
    call #BC77              ; CAS IN OPEN
    ret nc
    ld hl,#0040
    call #BC83              ; CAS IN DIRECT
    call #BC7A              ; CAS IN CLOSE
    di
    ; the 8x8 font from the lower ROM (#3800), chars 32-127 + a few symbols
    ld bc,#7F89             ; lower ROM on, upper off, mode 1
    out (c),c
    ld hl,#3800+32*8
    ld de,font
    ld bc,96*8
    ldir
    ld a,228                ; 128 heart
    call copy_glyph
    ld a,232                ; 129 empty box
    call copy_glyph
    ld a,233                ; 130 full box
    call copy_glyph
    ld a,7                  ; 131 lightning
    call copy_glyph
    ld a,224                ; 132 smiley
    call copy_glyph
    ld a,225                ; 133 sad face
    call copy_glyph
    ld bc,#7F8D
    out (c),c
    jp low_init

; A = ROM char, appended at DE
copy_glyph:
    ld l,a
    ld h,0
    add hl,hl
    add hl,hl
    add hl,hl
    ld bc,#3800
    add hl,bc
    ld bc,8
    ldir
    ret

low_name: db "LOW.BIN"
low_name_end:

font:
    defs (134-32)*8,0

    include "../build/sprites.asm"
    include "../build/texts.asm"
high_end:

    assert high_end <= EP_HI
    print "HIGH #4000-",{hex4}high_end," free ",EP_HI-high_end
    save "build/HIGH.BIN",#4000,high_end-#4000

; ============================================================================
; the episodes, each in its own memory space (packed by tools/pack_banks.py)
; ============================================================================
    include "../build/episodes.asm"
