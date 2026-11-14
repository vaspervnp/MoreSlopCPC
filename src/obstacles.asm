; ============================================================================
; The obstacles; each episode has some of them (ep_obst, OB_* bits):
;   pop-ups that cover part of the screen and swallow zaps
;   banners that fly across and swallow zaps (Mode 1 only)
;   "bros" who float down on bubbles and slow Themis down
; Their words come from the episode header (EH_*).
; ============================================================================

BR_ST   equ 0       ; 0 off, 1 floating, 2 walking, 3 falling
BR_X    equ 1
BR_YF   equ 2
BR_Y    equ 3
BR_T    equ 4
BR_SIZE equ 5

POPUP_W equ 28
POPUP_W0 equ 52         ; Mode 0: 12 characters of 4 bytes + the frame
POPUP_H equ 56
BAN_W   equ 40
BAN_H   equ 12

update_obstacles:
    ld a,(ep_obst)
    and OB_POP
    call nz,popup_tick
    ld a,(ep_obst)
    and OB_BAN
    call nz,ban_tick
    ld a,(ep_obst)
    and OB_BRO
    call nz,bros_tick
    ; time for a new one?
    ld hl,obst_timer
    dec (hl)
    ret nz
    ld a,(obst_int)
    ld (hl),a
    ; pick one of the episode's kinds that is not already out
    ld c,3
uo_try:
    push bc
    ld b,3
    call rand_mod
    pop bc
    ld b,a
    inc b
    ld a,1
uo_bit:
    dec b
    jr z,uo_got
    add a,a
    jr uo_bit
uo_got:
    ld b,a
    ld a,(ep_obst)
    and b
    jr z,uo_next
    cp OB_POP
    jr z,uo_pop
    cp OB_BAN
    jr z,uo_ban
    ; bro: one at a time (they are big sprites)
    ld a,(bros+BR_ST)
    or a
    jp z,bro_new
    jr uo_next
uo_pop:
    ld a,(popup_on)
    ld hl,ov_on
    or (hl)
    jp z,popup_new
    jr uo_next
uo_ban:
    ld a,(ban_on)
    or a
    jp z,banner_new
uo_next:
    dec c
    jr nz,uo_try
    ret

draw_obstacles:
    ld a,(ep_obst)
    and OB_BAN
    call nz,draw_banner
    ld a,(ep_obst)
    and OB_BRO
    ret z
    jp draw_bros

; B = bolt x, C = bolt y -> carry if an obstacle swallowed the zap
bolt_vs_obstacles:
    ld a,(ep_obst)
    and OB_POP
    jr z,bvo_1
    call bv_popup
    ret c
bvo_1:
    ld a,(ep_obst)
    and OB_BAN
    jr z,bvo_2
    call bv_banner
    ret c
bvo_2:
    ld a,(ep_obst)
    and OB_BRO
    ret z
    jp bv_bros

; ============================================================================
; pop-ups
; ============================================================================
popup_tick:
    ld a,(popup_on)
    or a
    ret z
    ld hl,popup_life
    dec (hl)
    ret nz
    jr popup_close

popup_new:
    ; Mode 1: x = 4 + 2*rand(25); Mode 0 (wider, 4 bytes per char): x = 4*rand(7)
    ld a,(cur_mode)
    or a
    jr z,pn_m0
    ld b,25
    call rand_mod
    add a,a
    add a,4
    jr pn_x
pn_m0:
    ld b,7
    call rand_mod
    add a,a
    add a,a
pn_x:
    ld (pp_x),a
    ld b,40
    call rand_mod
    add a,POPUP_MINY
    ld (pp_y),a
    ; one of the episode's variants (4 line pointers each)
    ld a,EH_POPT
    call ep_ptr
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
    ld (pp_txt),hl
    call popup_build
    ld hl,popup_cmds
    call ov_open
    ld a,1
    ld (popup_on),a
    ld a,3
    ld (popup_hp),a
    ld a,110
    ld (popup_life),a
    ld a,SFX_POPUP
    call play_sfx
    ld a,EH_POPIN
    jp ep_msg
popup_close:
    xor a
    ld (popup_on),a
    jp ov_close

; write the command list for a pop-up at (pp_x, pp_y)
popup_build:
    ld ix,popup_cmds
    ld a,(pp_x)
    ld b,a
    ld a,(pp_y)
    ld c,a
    ld a,(cur_mode)
    or a
    ld e,POPUP_W
    jr nz,pb_w
    ld e,POPUP_W0
pb_w:
    ; header
    ld (ix+0),#FF
    ld (ix+1),b
    ld (ix+2),c
    ld (ix+3),e
    ld (ix+4),POPUP_H
    ; white frame
    ld (ix+5),4
    ld (ix+6),b
    ld (ix+7),c
    ld (ix+8),e
    ld (ix+9),POPUP_H
    ld (ix+10),3
    ; title bar
    ld (ix+11),4
    ld a,b
    inc a
    ld (ix+12),a
    ld a,c
    inc a
    ld (ix+13),a
    ld a,e
    sub 2
    ld (ix+14),a
    ld (ix+15),9
    ld (ix+16),2
    ; inside
    ld (ix+17),4
    ld a,b
    inc a
    ld (ix+18),a
    ld a,c
    add a,11
    ld (ix+19),a
    ld a,e
    sub 2
    ld (ix+20),a
    ld (ix+21),POPUP_H-13
    ld (ix+22),0
    ; title text: column = x/2+1 (Mode 1) or x/4+1 (Mode 0)
    ld a,(cur_mode)
    or a
    ld a,b
    jr nz,pb_c1
    srl a
pb_c1:
    srl a
    inc a
    ld d,a                  ; text column
    ld (ix+23),3
    ld (ix+24),d
    ld a,c
    inc a
    ld (ix+25),a
    push de
    ld a,EH_POPTITLE
    call ep_ptr
    pop de
    ld (ix+26),l
    ld (ix+27),h
    ; four lines of text
    ld hl,(pp_txt)
    ld a,c
    add a,13
    ld e,a
    ld iy,popup_cmds+28
    ld b,4
pb_lp:
    ld (iy+0),3
    ld (iy+1),d
    ld (iy+2),e
    ld a,(hl)
    ld (iy+3),a
    inc hl
    ld a,(hl)
    ld (iy+4),a
    inc hl
    ld a,e
    add a,8
    ld e,a
    push de
    ld de,5
    add iy,de
    pop de
    djnz pb_lp
    ; the button
    ld (iy+0),3
    ld a,d
    add a,4
    ld (iy+1),a
    ld (iy+2),e
    ld hl,txt_popup_ok
    ld (iy+3),l
    ld (iy+4),h
    ld (iy+5),0
    ret

bv_popup:
    ld a,(popup_on)
    or a
    ret z
    ld d,BOLT_W
    ld e,BOLT_H
    call ov_hit
    ret nc
    call bolt_kill
    ld a,SFX_THUD
    call play_sfx
    ld hl,popup_hp
    dec (hl)
    jr nz,bvp_1
    call popup_close
    ld a,#30
    call add_score
    ld a,EH_POPDONE
    call ep_msg
bvp_1:
    scf
    ret

; ============================================================================
; banners
; ============================================================================
ban_tick:
    ld a,(ban_on)
    or a
    ret z
    jr ob_move

banner_new:
    ; pick a headline and paint the banner into ban_buf
    ld a,EH_HEADS
    call ep_ptr
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
    push hl
    call banner_paint
    pop hl
    ; lane and direction
    ld b,3
    call rand_mod
    ld b,a
    add a,a
    add a,b
    add a,a
    add a,a
    add a,a                 ; *24
    add a,78
    ld (ban_y),a
    call rand
    rra
    ld a,1
    ld b,-BAN_W
    jr c,ob_dir
    ld a,-1
    ld b,80
ob_dir:
    ld (ban_dx),a
    ld a,b
    ld (ban_x),a
    ld a,4
    ld (ban_hp),a
    ld a,1
    ld (ban_on),a
    ld a,SFX_POPUP
    call play_sfx
    ld a,EH_BANIN
    jp ep_msg
ob_move:
    ld a,(frame_ctr)
    and 1
    ld a,(difficulty)
    jr nz,ob_m1
    or a
    ret z                   ; easy: half speed
ob_m1:
    ld a,(ban_dx)
    ld b,a
    ld a,(ban_x)
    add a,b
    ld (ban_x),a
    bit 7,b
    jr nz,ob_left
    ; moving right: gone when x >= 80 (and positive)
    bit 7,a
    ret nz
    cp 80
    ret c
    jr ob_gone
ob_left:
    cp -BAN_W
    ret nz
ob_gone:
    xor a
    ld (ban_on),a
    ret

; HL = headline (20 chars) -> ban_buf
banner_paint:
    push hl
    ld hl,ban_buf
    ld bc,BAN_W*2
    ld a,#F0
    call memset
    ld hl,ban_buf+BAN_W*2
    ld bc,BAN_W*8
    ld a,#0F
    call memset
    ld hl,ban_buf+BAN_W*10
    ld bc,BAN_W*2
    ld a,#F0
    call memset
    ld hl,BAN_W
    ld (tl_stride),hl
    ld a,3
    ld (txt_fg),a
    ld a,2
    ld (txt_bg),a
    pop hl
    ld de,ban_buf+BAN_W*2
    jp text_m1_lin

; HL = dest, BC = count (>0), A = value
memset:
    ld (hl),a
    dec bc
    ld a,b
    or c
    ret z
    ld d,h
    ld e,l
    inc de
    ldir
    ret

draw_banner:
    ld a,(ban_on)
    or a
    ret z
    ld a,(ban_x)
    ld (op_x),a
    ld a,(ban_y)
    ld (op_y),a
    ld a,BAN_W
    ld (op_w),a
    ld a,BAN_H
    ld (op_h),a
    ld hl,ban_buf
    ld (op_src),hl
    jp draw_opaque_clip

bv_banner:
    ld a,(ban_on)
    or a
    ret z
    ; (bx - ban_x + 1) < BAN_W + 1 ?
    ld a,(ban_x)
    ld d,a
    ld a,b
    sub d
    inc a
    cp BAN_W+1
    ret nc
    ld a,(ban_y)
    ld d,a
    ld a,c
    sub d
    add a,BOLT_H-1
    cp BAN_H+BOLT_H-1
    ret nc
    call bolt_kill
    ld a,SFX_THUD
    call play_sfx
    ld hl,ban_hp
    dec (hl)
    jr nz,bvb_1
    xor a
    ld (ban_on),a
    ld a,#50
    call add_score
    ld a,EH_BANDONE
    call ep_msg
    ; a few poofs along it
    ld a,(ban_y)
    ld c,a
    ld a,(ban_x)
    ld b,4
bvb_p:
    push bc
    push af
    bit 7,a
    jr nz,bvb_skip
    cp 76
    jr nc,bvb_skip
    ld b,a
    call add_poof
bvb_skip:
    pop af
    pop bc
    add a,10
    djnz bvb_p
bvb_1:
    scf
    ret

; ============================================================================
; bros
; ============================================================================
bro_new:
    ld ix,bros              ; one bro at a time (they are big sprites)
    ld (ix+BR_ST),1
    ld b,74
    call rand_mod
    ld (ix+BR_X),a
    ld (ix+BR_Y),PLAY_TOP+20
    ld (ix+BR_YF),0
    ld (ix+BR_T),0
    ld a,EH_BROIN
    jp ep_msg

bros_tick:
    ld ix,bros
    call bro_tick
    ld ix,bros+BR_SIZE
bro_tick:
    ld a,(ix+BR_ST)
    or a
    ret z
    inc (ix+BR_T)
    dec a
    jr z,bt_float
    dec a
    jr z,bt_walk
    ; falling
    ld a,(ix+BR_Y)
    add a,5
    ld (ix+BR_Y),a
    add a,24
    cp SHELF_Y
    ret c
    ld (ix+BR_ST),0
    ld b,(ix+BR_X)
    ld c,PLAYER_Y
    jp add_poof
bt_float:
    ld a,(ix+BR_YF)
    add a,#90
    ld (ix+BR_YF),a
    ld a,(ix+BR_Y)
    adc a,0
    ld (ix+BR_Y),a
    add a,32
    cp SHELF_Y-2
    ret c
    ld (ix+BR_ST),2
    ld (ix+BR_Y),PLAYER_Y
    ld (ix+BR_T),0
    ret
bt_walk:
    ; gets bored after a while
    ld a,(ix+BR_T)
    cp 250
    jr c,bw_1
    ld (ix+BR_ST),0
    ld b,(ix+BR_X)
    ld c,PLAYER_Y
    call add_poof
    ld a,EH_BROLEFT
    jp ep_msg
bw_1:
    and 1
    jr nz,bw_touch
    ld a,(player_x)
    cp (ix+BR_X)
    jr z,bw_touch
    jr c,bw_l
    inc (ix+BR_X)
    jr bw_touch
bw_l:
    dec (ix+BR_X)
bw_touch:
    ; |player_x - x| < 4 ?
    ld a,(player_x)
    sub (ix+BR_X)
    add a,3
    cp 7
    ret nc
    ld (ix+BR_ST),0
    ld a,100
    ld (player_slow),a
    ld a,SFX_THUD
    call play_sfx
    ld b,(ix+BR_X)
    ld c,PLAYER_Y
    call add_poof
    ld a,EH_BROHIT
    jp ep_msg

draw_bros:
    ld ix,bros
    call draw_bro
    ld ix,bros+BR_SIZE
draw_bro:
    ld a,(ix+BR_ST)
    or a
    ret z
    dec a
    ld a,SS_BRO
    jr z,db_1
    ld a,(ix+BR_T)
    and 4
    rrca
    add a,SS_BRO+2
db_1:
    call spr_get
    ld b,(ix+BR_X)
    ld c,(ix+BR_Y)
    jp draw_masked

bv_bros:
    ld ix,bros
    call bv_bro
    ret c
    ld ix,bros+BR_SIZE
bv_bro:
    ld a,(ix+BR_ST)
    cp 1
    jr nz,bvr_no
    ; bubble: x .. x+6, y .. y+20
    ld a,b
    add a,BOLT_W
    cp (ix+BR_X)
    jr c,bvr_no
    jr z,bvr_no
    ld a,(ix+BR_X)
    add a,6
    cp b
    jr c,bvr_no
    jr z,bvr_no
    ld a,c
    add a,BOLT_H
    cp (ix+BR_Y)
    jr c,bvr_no
    jr z,bvr_no
    ld a,(ix+BR_Y)
    add a,20
    cp c
    jr c,bvr_no
    jr z,bvr_no
    call bolt_kill
    ld (ix+BR_ST),3
    ld a,SFX_POP
    call play_sfx
    ld a,#25
    call add_score
    ld a,EH_BRODONE
    call ep_msg
    scf
    ret
bvr_no:
    or a
    ret
