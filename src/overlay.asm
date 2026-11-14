; ============================================================================
; Overlays: boxes that sit on top of the playfield (cards, the AI pop-up).
;
; An overlay is drawn step by step, one command per buffer per frame, so it
; "generates" itself on screen. While it is up, sprites that touch its
; rectangle are not drawn, so nothing ever needs to repair it. Closing it
; copies the clean background back into each buffer.
;
; Command list:
;   header  db wcols, 0                - centred card, width in text columns
;     or    db #FF, x, y, w, h         - explicit rectangle (bytes / lines)
;   then for the centred form:  db y, h  (lines)
;   db 1, y, h, pen                    - fill the card width
;   db 2, y : dw text                  - text line, centred
;   db 3, col, y : dw text             - text at a column
;   db 4, x, y, w, h, pen              - fill an explicit rectangle (bytes)
;   db 0                               - end
; ============================================================================

; HL = command list
ov_open:
    ld a,(hl)
    inc hl
    cp #FF
    jr z,oo_explicit
    ; centred: A = width in columns (Mode 0 cards use all 20)
    ld b,a
    ld a,(cur_mode)
    or a
    jr nz,oo_m1
    ld b,20
oo_m1:
    ld a,b
    ld (ov_wcols),a
    ld a,(cur_mode)
    or a
    ld a,20
    jr z,oo_m0
    ld a,40
oo_m0:
    sub b
    srl a                   ; left column
    ld (ov_col),a
    call col_to_x
    ld (ov_x),a
    ld a,b
    call col_to_x
    ld (ov_w),a
    inc hl                  ; skip the 0
    ld a,(hl)
    inc hl
    ld (ov_y),a
    ld a,(hl)
    inc hl
    ld (ov_h),a
    jr oo_go
oo_explicit:
    ld de,ov_x
    ld bc,4
    ldir
    xor a
    ld (ov_col),a
oo_go:
    ld (ov_pc_c0),hl
    ld (ov_pc_80),hl
    xor a
    ld (ov_closing),a
    inc a
    ld (ov_on),a
    ret

; A = columns -> A = bytes in the playfield mode
col_to_x:
    push bc
    ld c,a
    add a,a
    ld b,a
    ld a,(cur_mode)
    or a
    ld a,b
    jr nz,ctx_1
    add a,a
ctx_1:
    pop bc
    ret

ov_close:
    ld a,(ov_on)
    or a
    ret z
    ld a,3
    ld (ov_closing),a
    ret

; B=x C=y D=w E=h -> carry if the rectangle touches the overlay
ov_hit:
    ld a,(ov_on)
    or a
    ret z                   ; carry clear
    push hl
    ld a,b
    add a,d
    ld l,a                  ; x + w
    ld a,(ov_x)
    cp l
    jr nc,oh_no             ; ov_x >= x+w
    ld h,a
    ld a,(ov_w)
    add a,h                 ; ov_x + ov_w
    ld l,a
    ld a,b
    cp l
    jr nc,oh_no             ; x >= ov_x+ov_w
    ld a,c
    add a,e
    ld l,a                  ; y + h
    ld a,(ov_y)
    cp l
    jr nc,oh_no
    ld h,a
    ld a,(ov_h)
    add a,h
    ld l,a
    ld a,c
    cp l
    jr nc,oh_no
    pop hl
    scf
    ret
oh_no:
    pop hl
    or a
    ret

; one step of the overlay for the current draw buffer
ov_step:
    ld a,(ov_on)
    or a
    ret z
    ld a,(draw_hi)
    cp SCR_C0
    ld c,1
    ld hl,ov_pc_c0
    jr z,os_buf
    ld c,2
    ld hl,ov_pc_80
os_buf:
    ld a,(ov_closing)
    or a
    jr z,os_draw
    and c
    ret z                   ; this buffer is already clean
    ld a,(ov_closing)
    xor c
    ld (ov_closing),a
    push af
    ld a,(ov_x)
    ld b,a
    ld a,(ov_y)
    ld c,a
    ld a,(ov_w)
    ld d,a
    ld a,(ov_h)
    ld e,a
    call restore_rect
    pop af
    ret nz
    ld (ov_on),a            ; both clean: overlay gone
    ret
os_draw:
    ld (os_slot),hl
    ld e,(hl)
    inc hl
    ld d,(hl)
    ld a,d
    or e
    ret z                   ; finished drawing in this buffer
    ex de,hl                ; HL = command
    ld a,2
    ld (os_budget),a
os_cmd:
    ld a,(hl)
    inc hl
    or a
    jr nz,os_c1
    ld hl,0
    jp os_save
os_c1:
    cp 1
    jr nz,os_c2
    ; fill card width: y, h, pen
    ld a,(ov_x)
    ld b,a
    ld a,(ov_w)
    ld d,a
    ld c,(hl)
    inc hl
    ld e,(hl)
    inc hl
    ld a,(hl)
    inc hl
    push hl
    bit 7,a                 ; pen | #80: inset by one byte each side
    jr z,os_c1b
    inc b
    dec d
    dec d
os_c1b:
    and #0F
    call pen_fill_byte
    call fill_rect
    pop hl
    ld a,(os_budget)
    sub 2
    jr os_next
os_c2:
    cp 2
    jr nz,os_c3
    ld c,(hl)
    inc hl
    ld e,(hl)
    inc hl
    ld d,(hl)
    inc hl
    push hl
    ex de,hl
    push hl
    call str_len
    ld b,a
    ld a,(cur_mode)
    or a
    ld a,20
    jr z,os_c2m
    ld a,40
os_c2m:
    sub b
    srl a
    ld b,a
    pop hl
    call text_pf
    pop hl
    jr os_text_done
os_c3:
    cp 3
    jr nz,os_c4
    ld b,(hl)
    inc hl
    ld c,(hl)
    inc hl
    ld e,(hl)
    inc hl
    ld d,(hl)
    inc hl
    push hl
    ex de,hl
    call text_pf
    pop hl
    jr os_text_done
os_c4:
    ld b,(hl)
    inc hl
    ld c,(hl)
    inc hl
    ld d,(hl)
    inc hl
    ld e,(hl)
    inc hl
    ld a,(hl)
    inc hl
    push hl
    call pen_fill_byte
    call fill_rect
    pop hl
    ld a,(os_budget)
    sub 2
    jr os_next
os_text_done:
    ld a,(os_budget)
    dec a
os_next:
    ld (os_budget),a
    jr z,os_save
    jp p,os_cmd
os_save:
    ex de,hl
    ld hl,(os_slot)
    ld (hl),e
    inc hl
    ld (hl),d
    ret

; A = pen -> A = byte filling 2 (Mode 0) or 4 (Mode 1) pixels with it
pen_fill_byte:
    push hl
    push de
    ld e,a
    ld a,(cur_mode)
    or a
    jr nz,pfb_m1
    ld d,0
    ld hl,m0_left
    add hl,de
    ld a,(hl)
    ld e,a
    srl a
    or e
    pop de
    pop hl
    ret
pfb_m1:
    ld a,e
    ld d,0
    rra
    jr nc,pfb_1
    ld d,#F0
pfb_1:
    rra
    ld a,d
    jr nc,pfb_2
    or #0F
pfb_2:
    pop de
    pop hl
    ret

; HL = string -> A = printable length
str_len:
    ld b,0
sl_lp:
    ld a,(hl)
    inc hl
    or a
    jr z,sl_end
    cp 3
    jr nc,sl_ch
    inc hl
    jr sl_lp
sl_ch:
    inc b
    jr sl_lp
sl_end:
    ld a,b
    ret
