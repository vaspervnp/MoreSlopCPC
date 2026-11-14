; ============================================================================
; Title menu: Mode 0 picture (unpacked from bank 7), rainbow rasters on the
; logo, rotating info panel, difficulty choice and a scroller.
; The clean picture stays in #8000 so the panel can be repaired from it.
; ============================================================================

PANEL_X     equ 4
PANEL_Y     equ 120
PANEL_W     equ 72
PANEL_H     equ 64
SCROLL_ADDR equ #C000+24*80
PAGE_TIME   equ 200

menu:
    ld sp,STACK_TOP
    ld hl,rast_black
    ld (raster_ptr),hl
    ld a,SNG_MENU
    call play_song
    call wait_vbl
    ; unpack the picture into #8000, then copy it to the visible #C000
    xor a                   ; directory entry 0
    ld de,#8000
    call unpack_entry
    ld hl,#8000
    ld de,#C000
    ld bc,#4000
    ldir
    ld a,SCR_C0
    ld (draw_hi),a
    call show_buffer
    ld hl,rast_menu
    ld (raster_ptr),hl
    xor a
    ld (menu_page),a
    ld (scr_col),a
    ld hl,scroll_text
    ld (scr_ptr),hl
    ld a,PAGE_TIME
    ld (page_timer),a
    call menu_draw_page
mn_loop:
    ; 25 fps
mn_w:
    ld a,(vbl_count)
    cp 2
    jr c,mn_w
    xor a
    ld (vbl_count),a
    call read_input
    call menu_rainbow
    call scroll_step
    ; difficulty keys
    ld c,#FF
    KEY KL_1,KB_1
    jr nz,mk_2
    ld c,0
mk_2:
    KEY KL_2,KB_2
    jr nz,mk_3
    ld c,1
mk_3:
    KEY KL_3,KB_3
    jr nz,mk_ud
    ld c,2
mk_ud:
    ld a,(inp_new)
    and IN_UP
    jr z,mk_dn
    ld a,(difficulty)
    or a
    jr z,mk_dn
    dec a
    ld c,a
mk_dn:
    ld a,(inp_new)
    and IN_DOWN
    jr z,mk_set
    ld a,(difficulty)
    cp 2
    jr z,mk_set
    inc a
    ld c,a
mk_set:
    ld a,c
    cp #FF
    jr z,mk_page
    ld hl,difficulty
    cp (hl)
    jr nz,mk_change
    ld a,(menu_page)
    or a
    jr z,mk_page
mk_change:
    ld (hl),c
    ld a,SFX_BLIP
    call play_sfx
    xor a
    ld (menu_page),a
    ld a,PAGE_TIME
    ld (page_timer),a
    call menu_draw_page
    jr mn_loop
mk_page:
    KEY KL_H,KB_H
    jr z,mk_next
    ld hl,page_timer
    dec (hl)
    jr nz,mk_fire
mk_next:
    ld a,PAGE_TIME
    ld (page_timer),a
    ld a,(menu_page)
    inc a
    cp MENU_NPAGES+1
    jr c,mk_p1
    xor a
mk_p1:
    ld (menu_page),a
    call menu_draw_page
mk_fire:
    ld a,(inp_new)
    and IN_FIRE
    jp z,mn_loop
    ; start!
    ld a,SFX_START
    call play_sfx
    ld b,25
mf_fl:
    push bc
    call wait_vbl
    call menu_rainbow
    call menu_rainbow
    pop bc
    djnz mf_fl
    jp game_start

; ----------------------------------------------------------------------------
menu_draw_page:
    ld bc,PANEL_X*256+PANEL_Y
    ld de,PANEL_W*256+PANEL_H
    call copy_80_c0
    ld a,(menu_page)
    or a
    jr nz,mdp_text
    ; difficulty page: title, 3 options, hiscore
    ld hl,txt_select
    ld bc,1*256+PANEL_Y+2
    call text_m0
    ld c,0
mdp_opt:
    push bc
    ld a,(difficulty)
    cp c
    ld a,14
    ld d,' '
    jr nz,mdp_o1
    ld a,1
    ld d,'>'
mdp_o1:
    ld (txt_fg),a
    xor a
    ld (txt_bg),a
    ld a,d
    ld (opt_buf),a
    ld a,c
    add a,a
    ld e,a
    ld d,0
    ld hl,diff_names
    add hl,de
    ld e,(hl)
    inc hl
    ld d,(hl)
    ld hl,opt_buf+1
    ex de,hl
    ; copy the name after the marker
mdp_cp:
    ld a,(hl)
    ld (de),a
    inc hl
    inc de
    or a
    jr nz,mdp_cp
    pop bc
    push bc
    ld a,c
    add a,a
    add a,c
    add a,a
    add a,a                 ; *12
    add a,PANEL_Y+16
    ld c,a
    ld b,1
    ld hl,opt_buf
    call text_m0_keep
    pop bc
    inc c
    ld a,c
    cp 3
    jr c,mdp_opt
    ; hi-score
    ld hl,hiscore
    ld de,num_buf
    call bcd6
    ld hl,txt_hiscore
    ld bc,3*256+PANEL_Y+54
    call text_m0
    ld hl,num_buf
    ld bc,12*256+PANEL_Y+54
    jp text_m0
mdp_text:
    ; pages 1-3: five lines of text
    dec a
    add a,a
    ld e,a
    ld d,0
    ld hl,menu_pages
    add hl,de
    ld a,(hl)
    inc hl
    ld h,(hl)
    ld l,a
    ld c,PANEL_Y+2
mdp_ln:
    ld e,(hl)
    inc hl
    ld d,(hl)
    inc hl
    ld a,d
    or e
    ret z
    push hl
    push bc
    ex de,hl
    push hl
    call str_len
    ld b,a
    ld a,20
    sub b
    srl a
    ld b,a
    pop hl
    pop de
    push de
    ld c,e
    call text_m0
    pop bc
    ld a,c
    add a,12
    ld c,a
    pop hl
    jr mdp_ln

; text_m0 but keeping the colours already in txt_fg / txt_bg
text_m0_keep:
    jp text_m0

; ----------------------------------------------------------------------------
; rainbow: pens 1-3 of each raster zone walk through the colour wheel
; ----------------------------------------------------------------------------
menu_rainbow:
    ld hl,rb_phase
    inc (hl)
    ld a,(hl)
    srl a
    srl a
    ld c,a                  ; base index
    ld ix,rz_menu1+3        ; pen 1 of zone 1
    call rb_zone
    inc c
    ld ix,rz_menu2+3
    call rb_zone
    inc c
    ld ix,rz_menu3+3
    call rb_zone
    inc c
    ld ix,rz_menu4+3
    call rb_zone
    inc c
    ld ix,rz_menu5+3
; IX = pen 1 colour slot, C = index
rb_zone:
    ld a,c
    call rb_col
    ld (ix+0),a
    ld a,c
    add a,3
    call rb_col
    ld (ix+1),a
    ld a,c
    add a,6
    call rb_col
    ld (ix+2),a
    ret
; A = index -> A = GA colour from the 10-colour wheel
rb_col:
    push hl
    push de
rbc_m:
    cp 10
    jr c,rbc_ok
    sub 10
    jr rbc_m
rbc_ok:
    ld e,a
    ld d,0
    ld hl,rainbow
    add hl,de
    ld a,(hl)
    pop de
    pop hl
    ret

; ----------------------------------------------------------------------------
; scroller on the last character row (Mode 0, pen 3 on pen 0)
; ----------------------------------------------------------------------------
scroll_step:
    ld a,3
    ld (txt_fg),a
    xor a
    ld (txt_bg),a
    call m0_build
    ld hl,SCROLL_ADDR+1
    ld b,8
ss_sh:
    push bc
    push hl
    ld d,h
    ld e,l
    dec de
    ld bc,79
    ldir
    pop hl
    ld a,h
    add a,8
    ld h,a
    pop bc
    djnz ss_sh
    ; the new column
    ld hl,(scr_ptr)
    ld a,(hl)
    or a
    jr nz,ss_ch
    ld hl,scroll_text
    ld (scr_ptr),hl
    ld a,(hl)
ss_ch:
    call glyph_addr         ; DE = glyph
    ld a,(scr_col)
    ld c,a
    ld hl,SCROLL_ADDR+79
    ld b,8
ss_col:
    push bc
    ld a,(de)
    inc de
    ; bring bits (7-2k, 6-2k) down to bits 1,0
    inc c
ss_rot:
    rlca
    rlca
    dec c
    jr nz,ss_rot
    and 3
    or m0_tab&#FF
    push de
    ld e,a
    ld d,m0_tab/256
    ld a,(de)
    pop de
    ld (hl),a
    ld a,h
    add a,8
    ld h,a
    pop bc
    djnz ss_col
    ld a,(scr_col)
    inc a
    and 3
    ld (scr_col),a
    ret nz
    ld hl,(scr_ptr)
    inc hl
    ld (scr_ptr),hl
    ret
