; ============================================================================
; HUD (always Mode 1, lines 0-31): score, lives, wave, shelf, and the show_msg
; that "streams" its messages two characters per frame like a chatbot.
; Values are redrawn only when they change, once in each buffer.
; ============================================================================

HF_SCORE    equ 1
HF_LIVES    equ 2
HF_INFO     equ 4
HF_SHELF    equ 8
HF_HI       equ 16
HF_LABELS   equ 32
HF_ALL      equ 63

; A = fields to redraw (in both buffers)
hud_mark:
    ld b,a
    ld a,(hud_pend_c0)
    or b
    ld (hud_pend_c0),a
    ld a,(hud_pend_80)
    or b
    ld (hud_pend_80),a
    ret

hud_step:
    ld a,(draw_hi)
    cp SCR_C0
    ld hl,hud_pend_c0
    jr z,hs_1
    ld hl,hud_pend_80
hs_1:
    ld a,(hl)
    ld (hl),0
    ld (hs_flags),a
    or a
    jr z,hs_ticker
    bit 5,a
    call nz,hud_labels
    ld a,(hs_flags)
    bit 0,a
    call nz,hud_score
    ld a,(hs_flags)
    bit 1,a
    call nz,hud_lives
    ld a,(hs_flags)
    bit 2,a
    call nz,hud_info
    ld a,(hs_flags)
    bit 3,a
    call nz,hud_shelf
    ld a,(hs_flags)
    bit 4,a
    call nz,hud_hi
hs_ticker:
    ; two characters of the show_msg per frame
    ld a,(draw_hi)
    cp SCR_C0
    ld hl,tick_pos_c0
    jr z,hs_2
    ld hl,tick_pos_80
hs_2:
    ld a,(hl)
    cp 200
    jr c,hs_typing
    ; a new message: wipe the row first, a quarter per frame
    sub 200
    ld b,a
    add a,a
    add a,a
    add a,b
    add a,a
    add a,a                 ; *20 bytes
    ld b,a
    ld a,(hl)
    inc a
    cp 204
    jr c,hs_w1
    xor a
hs_w1:
    ld (hl),a
    ld c,HUD_ROW_TICK
    ld de,20*256+8
    xor a
    jp fill_rect
hs_typing:
    ld b,a
    ld a,(tick_len)
    cp b
    ret z
    ret c
    ld a,b
    ld (hs_pos),a
    inc a
    ld (hl),a
    ld a,(hs_pos)
    ld c,a
    ld b,0
    ld hl,tick_buf
    add hl,bc
    ld de,tick_tmp+4
    ldi
    ld a,(tick_col)
    ld (tick_tmp+1),a
    ld hl,tick_tmp
    ld a,(hs_pos)
    ld b,a
    ld c,HUD_ROW_TICK
    jp text_m1

; HL = message (0-terminated, may start with TX_FG n): copy into the show_msg
show_msg:
    ld a,1
    ld (tick_col),a
    ld a,(hl)
    cp TX_FG
    jr nz,tk_1
    inc hl
    ld a,(hl)
    ld (tick_col),a
    inc hl
tk_1:
    ld de,tick_buf
    ld b,40
tk_lp:
    ld a,(hl)
    or a
    jr z,tk_pad
    ld (de),a
    inc hl
    inc de
    djnz tk_lp
    ld a,40
    ld (tick_len),a
    jr tk_done
tk_pad:
    ld a,40
    sub b
    ld (tick_len),a
    ld a,' '
tk_pl:
    ld (de),a
    inc de
    djnz tk_pl
tk_done:
    ld a,200
    ld (tick_pos_c0),a
    ld (tick_pos_80),a
    ret

; show_msg from a random entry of a message table: HL = table (db n, dw ...)
show_msg_rand:
    ld a,(hl)
    inc hl
    push hl
    ld b,a
    call rand_mod
    pop hl
    add a,a
    ld e,a
    ld d,0
    add hl,de
    ld a,(hl)
    inc hl
    ld h,(hl)
    ld l,a
    jr show_msg

; ----------------------------------------------------------------------------
hud_labels:
    xor a
    ld hl,last_sc_c0
    ld b,12
hlb_clr:
    ld (hl),a
    inc hl
    djnz hlb_clr
    ld hl,txt_hud_row0
    ld bc,0*256+HUD_ROW_SCORE
    call text_m1
    ld hl,txt_hud_row1
    ld bc,0*256+HUD_ROW_INFO
    jp text_m1

; only the digits that differ from what this buffer shows are drawn
hud_score:
    ld hl,score
    ld de,num_buf
    call bcd6
    ld a,(draw_hi)
    cp SCR_C0
    ld hl,last_sc_c0
    jr z,hsc_1
    ld hl,last_sc_80
hsc_1:
    ld de,num_buf+2
    ld b,6
hsc_lp:
    ld a,(de)
    cp (hl)
    jr z,hsc_same
    ld (hl),a
    ld (one_ch+2),a
    push hl
    push de
    push bc
    ld a,12
    sub b                   ; column 6..11
    ld b,a
    ld c,HUD_ROW_SCORE
    ld hl,one_ch
    call text_m1
    pop bc
    pop de
    pop hl
hsc_same:
    inc hl
    inc de
    djnz hsc_lp
    ret

hud_hi:
    ld hl,hiscore
    ld de,num_buf
    call bcd6
    ld hl,num_buf
    ld bc,34*256+HUD_ROW_SCORE
    jp text_m1

hud_lives:
    ld hl,str_buf
    ld (hl),TX_FG
    inc hl
    ld (hl),2
    inc hl
    ld a,(lives)
    ld b,6
hl_lp:
    ld c,' '
    or a
    jr z,hl_1
    ld c,128                ; heart
    dec a
hl_1:
    ld (hl),c
    inc hl
    djnz hl_lp
    ld (hl),0
    ld hl,str_buf
    ld bc,15*256+HUD_ROW_SCORE
    jp text_m1

hud_info:
    ; "EP1 WAVE2 SLOP 12" values
    ld hl,str_buf
    ld (hl),TX_FG
    inc hl
    ld (hl),3
    inc hl
    ld a,(episode)
    add a,'1'
    ld (hl),a
    inc hl
    ld (hl),0
    ld hl,str_buf
    ld bc,2*256+HUD_ROW_INFO
    call text_m1
    ld hl,str_buf+2
    ld a,(wave)
    add a,'1'
    ld (hl),a
    ld hl,str_buf
    ld bc,8*256+HUD_ROW_INFO
    call text_m1
    ld a,(quota_left)
    ld hl,str_buf+2
    call dec2
    ld (hl),0
    ld hl,str_buf
    ld bc,20*256+HUD_ROW_INFO
    jp text_m1

hud_shelf:
    ; one block per allowed miss: full = used
    ld hl,str_buf
    ld (hl),TX_FG
    inc hl
    ld (hl),2
    inc hl
    ld a,(miss_limit)
    ld b,a
    ld a,(misses)
    ld c,a
    ld d,6
hsh_lp:
    ld a,' '
    dec b
    jp m,hsh_put
    ld a,129                ; empty box
    ld e,a
    ld a,c
    or a
    ld a,e
    jr z,hsh_put
    dec c
    ld a,130                ; full box
hsh_put:
    ld (hl),a
    inc hl
    dec d
    jr nz,hsh_lp
    ld (hl),0
    ld hl,str_buf
    ld bc,32*256+HUD_ROW_INFO
    jp text_m1

; ----------------------------------------------------------------------------
; numbers
; ----------------------------------------------------------------------------
; HL = 3 BCD bytes (big end first), DE = buffer -> "\x01\x03dddddd\0"
bcd6:
    ld a,TX_FG
    ld (de),a
    inc de
    ld a,3
    ld (de),a
    inc de
    ld b,3
b6_lp:
    ld a,(hl)
    rrca
    rrca
    rrca
    rrca
    and #0F
    add a,'0'
    ld (de),a
    inc de
    ld a,(hl)
    and #0F
    add a,'0'
    ld (de),a
    inc de
    inc hl
    djnz b6_lp
    xor a
    ld (de),a
    ret

; A = 0..99 -> two digits at (HL), HL advanced
dec2:
    ld b,'0'-1
d2_lp:
    inc b
    sub 10
    jr nc,d2_lp
    add a,'0'+10
    ld (hl),b
    inc hl
    ld (hl),a
    inc hl
    ret

; add A (BCD 0-99) * mult to the score
add_score:
    ld (as_op+2),a
    xor a
    ld (as_op+1),a
    jr as_go
; add A (BCD 0-99) hundreds * mult
add_score100:
    ld (as_op+1),a
    xor a
    ld (as_op+2),a
as_go:
    ld a,(mult)
    ld b,a
as_lp:
    ld hl,score+2
    ld de,as_op+2
    ld a,(de)
    add a,(hl)
    daa
    ld (hl),a
    dec hl
    dec de
    ld a,(de)
    adc a,(hl)
    daa
    ld (hl),a
    dec hl
    ld a,(hl)
    adc a,0
    daa
    ld (hl),a
    djnz as_lp
    ld a,HF_SCORE
    jp hud_mark
