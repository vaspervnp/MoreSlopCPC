; ============================================================================
; Video: double buffer (#C000 / #8000), sprites, background restore, text.
;
; Every sprite drawn into a buffer appends its rectangle to that buffer's
; dirty list. Two frames later, when the same buffer is drawn again, those
; rectangles are copied back from the clean background in the extra bank
; (bg_cfg = #C4..#C6, seen at #4000), and then the new frame is drawn.
; ============================================================================

; B = x (bytes), C = y (lines) -> HL = address in the draw buffer. Uses DE.
get_addr:
    ld l,c
    ld h,0
    add hl,hl
    ld de,line_tab
    add hl,de
    ld a,(hl)
    inc hl
    ld h,(hl)
    ld l,a
    ld a,(draw_hi)
    or h
    ld h,a
    ld a,l
    add a,b
    ld l,a
    ret nc
    inc h
    ret

; ----------------------------------------------------------------------------
; frame pacing - 25 fps (two VSYNCs per frame)
; ----------------------------------------------------------------------------
; Wait until the buffer we are about to draw into is no longer displayed:
; the CRTC latches a new start address at the top of the next frame, so we
; wait for the line-34 interrupt that follows the flip.
begin_frame:
    ld a,(flip_zone)
    cp 1
    jr nz,bf_safe
    ; flipped in zone 1 (lines 294-33): if that was after the wrap the
    ; next line-34 tick comes before the latch, so wait for one more
    ld hl,zone2_ctr
    ld a,(flip_z2)
bf_v:
    cp (hl)
    jr z,bf_v
    ld a,(hl)
    ld (flip_z2),a
bf_safe:
    ld hl,zone2_ctr
    ld a,(flip_z2)
bf_wait:
    cp (hl)
    jr z,bf_wait
    ld a,(draw_hi)
    cp SCR_C0
    jr nz,bf_80
    ld hl,dlist_c0
    ld de,(dend_c0)
    jr bf_go
bf_80:
    ld hl,dlist_80
    ld de,(dend_80)
bf_go:
    push hl
    call restore_list
    pop hl
    ld (dirty_ptr),hl
    ret

end_frame:
    ld hl,(dirty_ptr)
    ld a,(draw_hi)
    cp SCR_C0
    jr nz,ef_80
    ld (dend_c0),hl
    jr ef_wait
ef_80:
    ld (dend_80),hl
ef_wait:
    ld a,(vbl_count)
    cp 2
    jr c,ef_wait
    jr z,ef_ontime
    ld hl,lag_count
    inc (hl)
ef_ontime:
    ld hl,(game_frames)
    inc hl
    ld (game_frames),hl
    xor a
    ld (vbl_count),a
    ld a,(draw_hi)
    call show_buffer
    ld a,(int_zone)
    ld (flip_zone),a
    ld a,(zone2_ctr)
    ld (flip_z2),a
    ld a,(draw_hi)
    xor #40
    ld (draw_hi),a
    ret

; A = #C0 / #80 -> CRTC start address
show_buffer:
    rrca
    rrca
    ld bc,#BC0C
    out (c),c
    inc b
    out (c),a
    ld bc,#BC0D
    out (c),c
    inc b
    xor a
    out (c),a
    ret

; wait for the next VSYNC tick
wait_vbl:
    ld hl,frame_ctr
    ld a,(hl)
wv_lp:
    cp (hl)
    jr z,wv_lp
    ret

; forget everything in both dirty lists (after a full background copy)
clear_dirty:
    ld hl,dlist_c0
    ld (dend_c0),hl
    ld hl,dlist_80
    ld (dend_80),hl
    ld hl,dlist_c0
    ld a,(draw_hi)
    cp SCR_C0
    jr z,cd_1
    ld hl,dlist_80
cd_1:
    ld (dirty_ptr),hl
    ret

; B=x C=y D=w E=h -> append to the dirty list (keeps all registers but A)
add_dirty:
    push hl
    ld hl,(dirty_ptr)
    ld (hl),b
    inc hl
    ld (hl),c
    inc hl
    ld (hl),d
    inc hl
    ld (hl),e
    inc hl
    ld (dirty_ptr),hl
    pop hl
    ret

; ----------------------------------------------------------------------------
; restore rectangles from the background bank
; ----------------------------------------------------------------------------
; HL = list start, DE = list end
restore_list:
    ld a,l
    cp e
    jr nz,rl_any
    ld a,h
    cp d
    ret z
rl_any:
    push hl
    push de
    ld a,(bg_cfg)
    call set_cfg
    ld a,(draw_hi)
    sub #40
    ld (rr_dv+1),a
    pop de
    pop hl
rl_lp:
    ld a,l
    cp e
    jr nz,rl_do
    ld a,h
    cp d
    jr z,rl_end
rl_do:
    ld b,(hl)
    inc hl
    ld c,(hl)
    inc hl
    ld a,b
    ld (rr_x),a
    ld a,c
    ld (rr_y),a
    ld a,(hl)
    inc hl
    push hl
    push de
    ld d,a
    ld a,(hl)
    ld e,a
    call rr_core
    pop de
    pop hl
    inc hl
    jr rl_lp
rl_end:
    ld a,CFG_BASE
    jp set_cfg

; B=x C=y D=w E=h: copy from the background bank to the draw buffer
restore_rect:
    push bc
    push de
    ld a,(bg_cfg)
    call set_cfg
    ld a,(draw_hi)
    sub #40
    ld (rr_dv+1),a
    pop de
    pop bc
    ld a,b
    ld (rr_x),a
    ld a,c
    ld (rr_y),a
    call rr_core
    ld a,CFG_BASE
    jp set_cfg

; B=x C=y D=w E=h: copy the same rectangle from #8000 to #C000 (menu)
copy_80_c0:
    ld a,SCR_C0
    ld (draw_hi),a
    ld a,#40
    ld (rr_dv+1),a
    ld a,b
    ld (rr_x),a
    ld a,c
    ld (rr_y),a
    ; fall into rr_core

; D=w E=h, position in rr_x/rr_y; source = destination - (rr_dv) in the
; high byte. Each row is an unrolled LDI chain entered at (end - 2*w).
rr_core:
    ld a,d
    add a,a
    ld c,a
    ld b,0
    ld hl,rr_ldi_end
    or a
    sbc hl,bc
    ld (rr_call+1),hl
    ld a,e
    ld (rr_cnt),a
    ld a,(rr_x)
    ld b,a
    ld a,(rr_y)
    ld c,a
    call get_addr           ; HL = destination
    ex de,hl                ; DE = destination
rr_row:
    ld h,d
    ld l,e
    ld a,h
rr_dv:
    sub #80
    ld h,a                  ; HL = source
    push de
rr_call:
    call rr_ldi_end
    pop de
    NEXTLINE_DE
    ld hl,rr_cnt
    dec (hl)
    jr nz,rr_row
    ret

rr_ldi:
    repeat 80
    ldi
    rend
rr_ldi_end:
    ret

; copy the whole background bank to both screens
bg_to_screens:
    ld a,(bg_cfg)
    call set_cfg
    ld hl,BANK_WIN
    ld de,#C000
    ld bc,#4000
    ldir
    ld hl,BANK_WIN
    ld de,#8000
    ld bc,#4000
    ldir
    ld a,CFG_BASE
    jp set_cfg

; ----------------------------------------------------------------------------
; masked sprite: B = x, C = y, DE = sprite (db w, h, then mask/data pairs)
; ----------------------------------------------------------------------------
draw_masked:
    ld a,(de)
    ld (dm_w),a
    inc de
    ld a,(de)
    ld (dm_h),a
    inc de
    ld a,(de)               ; trimmed: offset of the block in the frame
    add a,b
    ld b,a
    inc de
    ld a,(de)
    add a,c
    ld c,a
    inc de
    ld (dm_src),de
    ld a,(dm_w)
    ld d,a
    ld a,(dm_h)
    ld e,a
    call ov_hit
    ret c
    call add_dirty
    call get_addr
    ex de,hl                ; DE = screen
    ; jump into the unrolled loop: entry = dm_unroll_end - 7*w
    ld a,(dm_w)
    ld b,a
    add a,a
    add a,a
    add a,a
    sub b
    ld c,a
    ld b,0
    ld hl,dm_unroll_end
    or a
    sbc hl,bc
    push ix
    push hl
    pop ix                  ; IX = entry into the unrolled loop
    ld hl,(dm_src)
    ld a,(dm_h)
    ld c,a
dm_row:
    push de
    jp (ix)
dm_back:
    pop de
    NEXTLINE_DE
    dec c
    jr nz,dm_row
    pop ix
    ret

; one byte = 7 bytes of code: screen AND mask OR data
dm_unroll:
    repeat 10
    ld a,(de)
    and (hl)
    inc hl
    or (hl)
    inc hl
    ld (de),a
    inc de
    rend
dm_unroll_end:
    jp dm_back

; ----------------------------------------------------------------------------
; opaque block with horizontal clipping (banner)
;   op_x (signed), op_y, op_w, op_h, op_src (linear, stride op_w)
; ----------------------------------------------------------------------------
draw_opaque_clip:
    ld hl,(op_src)
    ld a,(op_w)
    ld d,a                  ; visible width
    ld a,(op_x)
    bit 7,a
    jr z,doc_left_ok
    ; x < 0: skip -x bytes
    neg
    cp d
    ret nc
    ld c,a
    ld b,0
    add hl,bc
    ld a,d
    sub c
    ld d,a
    xor a
doc_left_ok:
    ld b,a                  ; x
    cp 80
    ret nc
    ; clip the right side: x + w > 80 ?
    add a,d
    sub 80
    jr c,doc_right_ok
    jr z,doc_right_ok
    ld c,a
    ld a,d
    sub c
    ld d,a
doc_right_ok:
    ld a,d
    or a
    ret z
    ld (op_vis),a
    ld (op_s2),hl
    ld a,(op_y)
    ld c,a
    ld a,(op_h)
    ld e,a
    call add_dirty
    call get_addr           ; HL = screen
    ld a,(op_h)
    ld (rr_cnt),a
    ld de,(op_s2)
doc_row:
    push hl
    push de
    ex de,hl
    ld a,(op_vis)
    ld c,a
    ld b,0
    ldir
    pop hl
    ld a,(op_w)
    ld c,a
    add hl,bc
    ex de,hl
    pop hl
    NEXTLINE
    ld a,(rr_cnt)
    dec a
    ld (rr_cnt),a
    jr nz,doc_row
    ret

; B=x C=y D=w E=h, A = fill byte (not recorded as dirty)
fill_rect:
    ld (fr_val+1),a
    ld a,d
    ld (fr_w+1),a
    ld a,e
    ld (rr_cnt),a
    call get_addr
fr_row:
    push hl
fr_w:
    ld b,0
fr_val:
    ld a,0
fr_col:
    ld (hl),a
    inc hl
    djnz fr_col
    pop hl
    NEXTLINE
    ld a,(rr_cnt)
    dec a
    ld (rr_cnt),a
    jr nz,fr_row
    ret

; ----------------------------------------------------------------------------
; LZ unpacker (format in tools/cpcgfx.py): HL = source, DE = destination
; ----------------------------------------------------------------------------
lz_unpack:
    ld a,(hl)
    inc hl
    bit 7,a
    jr nz,lz_match
    ld c,a
    ld b,0
    inc bc
    ldir
    jr lz_unpack
lz_match:
    and #7F
    add a,3
    ld c,a
    ld b,0
    ld a,(hl)
    inc hl
    push hl
    ld h,(hl)
    ld l,a
    or h
    jr z,lz_end
    push de
    ex de,hl
    or a
    sbc hl,de               ; HL = dst - offset
    pop de
    ldir
    pop hl
    inc hl
    jr lz_unpack
lz_end:
    pop hl
    ret

; ----------------------------------------------------------------------------
; text - font: 8x8, chars 32..132 at `font`
; strings: 0 ends, TX_FG n / TX_BG n change colours
; ----------------------------------------------------------------------------

; A = char -> DE = glyph
glyph_addr:
    sub 32
    ld e,a
    ld d,0
    ex de,hl
    add hl,hl
    add hl,hl
    add hl,hl
    ld de,font
    add hl,de
    ex de,hl
    ret

; build the Mode 1 nibble table for txt_fg / txt_bg
m1_build:
    push hl
    push bc
    push de
    ld a,(txt_fg)
    ld b,a
    ld a,(txt_bg)
    rlca
    rlca
    or b
    ld hl,m1_built
    cp (hl)
    jr z,mb_done
    ld (hl),a
    ld hl,m1_tab
    ld c,0
mb_lp:
    ld a,(txt_fg)
    ld b,c
    call m1_expand
    ld d,e
    ld a,c
    xor 15
    ld b,a
    ld a,(txt_bg)
    call m1_expand
    ld a,e
    or d
    ld (hl),a
    inc l
    inc c
    ld a,c
    cp 16
    jr nz,mb_lp
mb_done:
    pop de
    pop bc
    pop hl
    ret
; A = pen, B = nibble -> E
m1_expand:
    ld e,0
    bit 0,a
    jr z,me_1
    push af
    ld a,b
    rlca
    rlca
    rlca
    rlca
    ld e,a
    pop af
me_1:
    bit 1,a
    ret z
    ld a,e
    or b
    ld e,a
    ret

; build the Mode 0 pair table
m0_build:
    push hl
    push de
    ld hl,m0_left
    ld a,(txt_bg)
    ld e,a
    ld d,0
    add hl,de
    ld e,(hl)               ; L(bg)
    ld hl,m0_left
    ld a,(txt_fg)
    ld c,a
    ld b,0
    add hl,bc
    ld d,(hl)               ; L(fg)
    ; idx 0 = bg bg, 1 = bg fg, 2 = fg bg, 3 = fg fg   (bit1 = left)
    ld hl,m0_tab
    ld a,e
    srl a
    or e
    ld (hl),a               ; L(bg)|R(bg)
    inc l
    ld a,d
    srl a
    or e
    ld (hl),a               ; L(bg)|R(fg)
    inc l
    ld a,e
    srl a
    or d
    ld (hl),a               ; L(fg)|R(bg)
    inc l
    ld a,d
    srl a
    or d
    ld (hl),a
    pop de
    pop hl
    ret

; HL = string, B = column (Mode 1: 0-39), C = y. Draws into the draw buffer.
text_m1:
    push hl
    ld a,b
    add a,a
    ld b,a
    call get_addr
    ld (tx_scr),hl
    call m1_build
    pop hl
tm1_lp:
    ld a,(hl)
    inc hl
    or a
    ret z
    cp 3
    jr nc,tm1_ch
    call tx_ctrl
    call m1_build
    jr tm1_lp
tm1_ch:
    push hl
    call glyph_addr
    ld hl,(tx_scr)
    push hl
    ex de,hl                ; HL = glyph, DE = screen
    ld b,m1_tab/256
    ld a,8
    ld (tx_rows),a
tm1_row:
    ld a,(hl)
    inc hl
    push af
    rrca
    rrca
    rrca
    rrca
    and #0F
    ld c,a
    ld a,(bc)
    ld (de),a
    inc de
    pop af
    and #0F
    ld c,a
    ld a,(bc)
    ld (de),a
    dec de
    NEXTLINE_DE
    ld a,(tx_rows)
    dec a
    ld (tx_rows),a
    jr nz,tm1_row
    pop hl
    inc hl
    inc hl
    ld (tx_scr),hl
    pop hl
    jr tm1_lp

; A = control code (1/2), (HL) = argument
tx_ctrl:
    cp TX_FG
    ld a,(hl)
    inc hl
    jr nz,txc_bg
    ld (txt_fg),a
    ret
txc_bg:
    ld (txt_bg),a
    ret

; HL = string, B = column (Mode 0: 0-19), C = y
text_m0:
    push hl
    ld a,b
    add a,a
    add a,a
    ld b,a
    call get_addr
    ld (tx_scr),hl
    call m0_build
    pop hl
tm0_lp:
    ld a,(hl)
    inc hl
    or a
    ret z
    cp 3
    jr nc,tm0_ch
    call tx_ctrl
    call m0_build
    jr tm0_lp
tm0_ch:
    push hl
    call glyph_addr
    ld hl,(tx_scr)
    push hl
    ex de,hl
    ld b,m0_tab/256
    ld a,8
    ld (tx_rows),a
tm0_row:
    ld a,(hl)
    inc hl
    push hl
    ld l,a
    repeat 4
    ld a,l
    rlca
    rlca
    ld l,a
    and 3
    or m0_tab&#FF
    ld c,a
    ld a,(bc)
    ld (de),a
    inc de
    rend
    pop hl
    dec de
    dec de
    dec de
    dec de
    NEXTLINE_DE
    ld a,(tx_rows)
    dec a
    ld (tx_rows),a
    jr nz,tm0_row
    pop hl
    ld bc,4
    add hl,bc
    ld (tx_scr),hl
    pop hl
    jr tm0_lp

; text in the mode of the playfield (cur_mode): B = column in that mode
text_pf:
    ld a,(cur_mode)
    or a
    jp z,text_m0
    jp text_m1

; Mode 1 text into a linear buffer: HL = string, DE = buffer, stride in (tl_stride)
text_m1_lin:
    push de
    call m1_build
    pop de
tl_lp:
    ld a,(hl)
    inc hl
    or a
    ret z
    cp 3
    jr nc,tl_ch
    push de
    call tx_ctrl
    call m1_build
    pop de
    jr tl_lp
tl_ch:
    push hl
    push de
    call glyph_addr         ; DE = glyph
    ex de,hl                ; HL = glyph
    pop de
    push de
    ld b,m1_tab/256
    ld a,8
    ld (tx_rows),a
tl_row:
    ld a,(hl)
    inc hl
    push af
    rrca
    rrca
    rrca
    rrca
    and #0F
    ld c,a
    ld a,(bc)
    ld (de),a
    inc de
    pop af
    and #0F
    ld c,a
    ld a,(bc)
    ld (de),a
    dec de
    push hl
    ld hl,(tl_stride)
    add hl,de
    ex de,hl
    pop hl
    ld a,(tx_rows)
    dec a
    ld (tx_rows),a
    jr nz,tl_row
    pop de
    inc de
    inc de
    pop hl
    jr tl_lp
