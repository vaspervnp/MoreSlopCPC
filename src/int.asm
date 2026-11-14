; ============================================================================
; Interrupts: 300 Hz, six per frame.
;   zone 0  - 2 lines after VSYNC (line ~242): frame tick, music, keyboard
;   zone 1  - line ~294 (top border): palette/mode for the top of the screen
;   zone 2  - screen line ~34
;   zone 3  - screen line ~86
;   zone 4  - screen line ~138
;   zone 5  - screen line ~190
; raster_ptr points to 6 words, one entry per zone (0 = leave as is).
; An entry is: db ga_mode_or_0, count, colour*count  (pens from 0 up)
; ============================================================================

int_handler:
    push af
    push bc
    push hl
    ld b,#F5
    in a,(c)
    rra
    jr nc,ih_next
    xor a
    jr ih_set
ih_next:
    ld a,(int_zone)
    inc a
    cp 6
    jr c,ih_set
    ld a,5
ih_set:
    ld (int_zone),a
    add a,a
    ld l,a
    ld h,0
    ld bc,(raster_ptr)
    add hl,bc
    ld a,(hl)
    inc hl
    ld h,(hl)
    ld l,a
    or h
    call nz,set_raster
    ld a,(int_zone)
    or a
    jr z,ih_frame
    pop hl
    pop bc
    pop af
    ei
    ret

ih_frame:
    push de
    push ix
    push iy
    ld bc,#7F00+CFG_BASE
    out (c),c
    ld hl,vbl_count
    inc (hl)
    ld hl,frame_ctr
    inc (hl)
    call music_tick
    call read_matrix
    ld a,(cur_cfg)
    ld b,#7F
    out (c),a
    pop iy
    pop ix
    pop de
    pop hl
    pop bc
    pop af
    ei
    ret

; HL = raster entry
set_raster:
    ld b,#7F
    ld a,(hl)
    inc hl
    or a
    jr z,sr_nomode
    out (c),a
sr_nomode:
    ld a,(hl)
    inc hl
    or a
    ret z
    push de
    ld d,a
    ld c,0
sr_lp:
    out (c),c
    ld a,(hl)
    inc hl
    out (c),a
    inc c
    dec d
    jr nz,sr_lp
    pop de
    ret

; ----------------------------------------------------------------------------
; keyboard: read the 10 matrix lines into keymap (active low)
; ----------------------------------------------------------------------------
read_matrix:
    ld bc,#F40E
    out (c),c
    ld bc,#F6C0
    out (c),c
    ld bc,#F600
    out (c),c
    ld bc,#F792
    out (c),c
    ld hl,keymap
    ld e,#40
    ld d,10
rm_lp:
    ld b,#F6
    out (c),e
    ld b,#F4
    in a,(c)
    ld (hl),a
    inc hl
    inc e
    dec d
    jr nz,rm_lp
    ld bc,#F782
    out (c),c
    ld bc,#F600
    out (c),c
    ret

; ----------------------------------------------------------------------------
; set_cfg: A = RAM configuration (#C0, #C4-#C7)
; ----------------------------------------------------------------------------
set_cfg:
    ld (cur_cfg),a
    ld b,#7F
    out (c),a
    ret
