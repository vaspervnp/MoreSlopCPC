; ============================================================================
; The game: Themis zaps the slop the SlopBot prints before it hits the shelf.
; ============================================================================

IN_LEFT     equ 1
IN_RIGHT    equ 2
IN_UP       equ 4
IN_DOWN     equ 8
IN_FIRE     equ 16
IN_ESC      equ 32
IN_PAUSE    equ 64

; difficulty table entry
DF_LIVES    equ 0
DF_MISSES   equ 1
DF_FALL     equ 2   ; word, 8.8 lines per frame
DF_FALLINC  equ 4   ; per level
DF_SPAWN    equ 5   ; frames between prints
DF_MAX      equ 6
DF_QUOTA    equ 7
DF_OBST     equ 8   ; frames between obstacles
DF_COOL     equ 9   ; zap cooldown
DF_SIZE     equ 10

REV_TIME    equ 125     ; frames of reversed controls after zapping a deepfake
BEAT_EVERY  equ 250     ; frames between bass drops
DROP_TIME   equ 50      ; frames a bass drop lasts
BOSS_HP     equ 12      ; zaps to bring down the SlopBot

; ----------------------------------------------------------------------------
; input -> inp / inp_new
; ----------------------------------------------------------------------------
read_input:
    ld c,0
    KEY KL_LEFT,KB_LEFT
    jr nz,ri_1
    set 0,c
ri_1:
    KEY KL_A,KB_A
    jr nz,ri_2
    set 0,c
ri_2:
    KEY KL_JOY,KB_JLEFT
    jr nz,ri_3
    set 0,c
ri_3:
    KEY KL_RIGHT,KB_RIGHT
    jr nz,ri_4
    set 1,c
ri_4:
    KEY KL_D,KB_D
    jr nz,ri_5
    set 1,c
ri_5:
    KEY KL_JOY,KB_JRIGHT
    jr nz,ri_6
    set 1,c
ri_6:
    KEY KL_UP,KB_UP
    jr nz,ri_7
    set 2,c
ri_7:
    KEY KL_JOY,KB_JUP
    jr nz,ri_8
    set 2,c
ri_8:
    KEY KL_DOWN,KB_DOWN
    jr nz,ri_9
    set 3,c
ri_9:
    KEY KL_JOY,KB_JDOWN
    jr nz,ri_10
    set 3,c
ri_10:
    KEY KL_SPACE,KB_SPACE
    jr nz,ri_11
    set 4,c
ri_11:
    ld a,(keymap+KL_JOY)
    and KB_JFIRE
    cp KB_JFIRE
    jr z,ri_12
    set 4,c
ri_12:
    KEY KL_RETURN,KB_RETURN
    jr nz,ri_13
    set 4,c
ri_13:
    KEY KL_ESC,KB_ESC
    jr nz,ri_14
    set 5,c
ri_14:
    KEY KL_P,KB_P
    jr nz,ri_15
    set 6,c
ri_15:
    ld a,(inp)
    cpl
    and c
    ld (inp_new),a
    ld a,c
    ld (inp),a
    ret

; ----------------------------------------------------------------------------
; random numbers (xorshift16)
; ----------------------------------------------------------------------------
rand:
    push hl
    ld hl,(seed)
    ld a,h
    rra
    ld a,l
    rra
    xor h
    ld h,a
    ld a,l
    rra
    ld a,h
    rra
    xor l
    ld l,a
    xor h
    ld h,a
    ld (seed),hl
    pop hl
    ret

; B = n -> A = random 0..n-1   (high byte of rand * n). Uses DE, HL.
rand_mod:
    call rand
    ld h,a
    ld l,0
    ld d,0
    ld e,b
    ld b,8
rmd_lp:
    add hl,hl
    jr nc,rmd_s
    add hl,de
rmd_s:
    djnz rmd_lp
    ld a,h
    ret

; ----------------------------------------------------------------------------
; sprite set lookup: A = offset (SS_...) -> DE = sprite
; ----------------------------------------------------------------------------
spr_get:
    ld hl,(cur_set)
    ld e,a
    ld d,0
    add hl,de
    ld e,(hl)
    inc hl
    ld d,(hl)
    ret

; ============================================================================
; game flow
; ============================================================================
game_start:
    ; difficulty parameters
    ld a,(difficulty)
    ld b,a
    add a,a
    add a,a
    add a,b
    add a,a                 ; *10
    ld e,a
    ld d,0
    ld hl,diff_tab
    add hl,de
    ld (diff_ptr),hl
    ld a,(hl)
    ld (lives),a
    inc hl
    ld a,(hl)
    ld (miss_limit),a
    xor a
    ld (score),a
    ld (score+1),a
    ld (score+2),a
    ld (wave),a
    ld (loop_n),a
    ld (quit_flag),a
    ld a,(start_ep)         ; 0 unless a test asks for another episode
    ld (episode),a
    ld a,(frame_ctr)
    ld hl,(seed)
    xor l
    ld l,a
    or h
    jr nz,gs_seed
    inc l
gs_seed:
    ld (seed),hl
    call episode_start
    jp game_loop

; set up the current episode and show its intro card
episode_start:
    call ep_load
    call clear_dirty
    call reset_objects
    ld hl,(ep_raster)
    ld (raster_ptr),hl
    call ep_colours
    ld a,HF_ALL
    call hud_mark
    ld a,SNG_EP
    call play_song
    ld hl,(ep_card)
    call ov_open
    call wave_setup
    ld hl,msg_get_ready
    call show_msg
    ld a,ST_INTRO
    ld (state),a
    ld a,200
    ld (state_timer),a
    ret

; remember pen 0 of the playfield and pen 1 of the shelf (for flashes)
ep_colours:
    ld hl,(ep_raster)
    ld de,4
    add hl,de
    ld e,(hl)
    inc hl
    ld d,(hl)
    inc de
    inc de
    ld a,(de)
    ld (ep_pen0),a
    ld hl,(ep_raster)
    ld de,10
    add hl,de
    ld e,(hl)
    inc hl
    ld d,(hl)
    ld a,d
    or e
    ret z
    inc de
    inc de
    inc de
    ld a,(de)
    ld (ep_shelf1),a
    ret

reset_objects:
    ld hl,items
    ld de,items+1
    ld bc,objects_end-items-1
    ld (hl),0
    ldir
    ld a,37
    ld (player_x),a
    ld a,20
    ld (robot_x),a
    ld a,1
    ld (robot_dx),a
    ld (mult),a
    xor a
    ld (streak),a
    ld (misses),a
    ld (ov_on),a
    ld (ov_closing),a
    ld (popup_on),a
    ld a,40
    ld (spawn_timer),a
    ld a,BEAT_EVERY
    ld (beat_timer),a
    ret

; compute the wave parameters from difficulty, episode, wave and loop
wave_setup:
    xor a
    ld (boss_on),a
    ; level = loop*30 + episode*3 + wave
    ld a,(loop_n)
    add a,a
    ld b,a                  ; 2*loop
    add a,a
    add a,a
    add a,a
    add a,a                 ; 32*loop
    sub b
    ld b,a
    ld a,(episode)
    ld c,a
    add a,a
    add a,c
    add a,b
    ld b,a
    ld a,(wave)
    add a,b
    ld (level),a
    ld ix,(diff_ptr)
    ; fall speed = base + level * inc
    ld l,(ix+DF_FALL)
    ld h,(ix+DF_FALL+1)
    ld e,(ix+DF_FALLINC)
    ld d,0
    ld a,(level)
    or a
    jr z,ws_f2
    ld b,a
ws_f1:
    add hl,de
    djnz ws_f1
ws_f2:
    ld a,h
    cp 4
    jr c,ws_f3
    ld hl,#0400
ws_f3:
    ld (fall_spd),hl
    ; spawn interval = base - level (min 9)
    ld a,(level)
    ld b,a
    ld a,(ix+DF_SPAWN)
    sub b
    jr c,ws_s1
    cp 9
    jr nc,ws_s2
ws_s1:
    ld a,9
ws_s2:
    ld (spawn_int),a
    ; max items = base + level/5 (max 8)
    ld a,(level)
    ld b,0
ws_m1:
    sub 5
    jr c,ws_m2
    inc b
    jr ws_m1
ws_m2:
    ld a,(cur_mode)
    or a
    ld a,(ix+DF_MAX)
    jr nz,ws_m2b
    dec a                   ; Mode 0 sprites are wider: one item fewer
ws_m2b:
    add a,b
    cp MAX_ITEMS+1
    jr c,ws_m3
    ld a,MAX_ITEMS
ws_m3:
    ld (item_cap),a
    ; quota = base + 4*wave + 4*loop
    ld a,(wave)
    ld b,a
    ld a,(loop_n)
    add a,b
    add a,a
    add a,a
    add a,(ix+DF_QUOTA)
    ld (quota_left),a
    ; obstacles = base - 3*level (min 60)
    ld a,(level)
    ld b,a
    add a,a
    add a,b
    ld b,a
    ld a,(ix+DF_OBST)
    sub b
    jr c,ws_o1
    cp 60
    jr nc,ws_o2
ws_o1:
    ld a,60
ws_o2:
    ld (obst_int),a
    ld (obst_timer),a
    ld a,(ix+DF_COOL)
    ld (cool_max),a
    ld a,HF_INFO|HF_SHELF|HF_LIVES
    jp hud_mark

; ----------------------------------------------------------------------------
; main loop
; ----------------------------------------------------------------------------
game_loop:
    call read_input
    ld a,(state)
    cp ST_PAUSE
    jr z,gl_pause
    ld a,(inp_new)
    and IN_PAUSE
    jr z,gl_nopause
    ld a,(state)
    cp ST_PLAY
    jr nz,gl_nopause
    ld a,ST_PAUSE
    ld (state),a
    ld hl,msg_paused
    call show_msg
    jr gl_draw
gl_nopause:
    ld a,(inp_new)
    and IN_ESC
    jr z,gl_noesc
    ld a,1
    ld (quit_flag),a
gl_noesc:
    call update_state
    jr gl_draw
gl_pause:
    ld a,(inp_new)
    and IN_PAUSE|IN_FIRE
    jr z,gl_draw
    ld a,ST_PLAY
    ld (state),a
    ld hl,msg_unpaused
    call show_msg
gl_draw:
    call begin_frame
    call draw_world
    call ov_step
    call hud_step
    call flash_step
    call end_frame
    ld a,(quit_flag)
    or a
    jr z,game_loop
    ; back to the menu
    call update_hiscore
    jp menu

update_hiscore:
    ld hl,score
    ld de,hiscore
    ld b,3
uh_lp:
    ld a,(de)
    cp (hl)
    jr c,uh_new
    ret nz
    inc hl
    inc de
    djnz uh_lp
    ret
uh_new:
    ld hl,score
    ld de,hiscore
    ld bc,3
    ldir
    ret

update_state:
    ld a,(state)
    or a
    jp z,do_intro
    dec a
    jp z,do_play
    dec a
    jp z,do_clear
    dec a
    jp z,do_lost
    dec a
    jp z,do_over
    jp do_win

; ---- intro card: wait for fire or the timer
do_intro:
    call update_player
    call update_robot
    call update_poofs
    ld a,(inp_new)
    and IN_FIRE
    jr nz,si_go
    ld hl,state_timer
    dec (hl)
    ret nz
si_go:
    call ov_close
    ld a,ST_PLAY
    ld (state),a
    ld a,SFX_START
    call play_sfx
    ld hl,msg_wave
    call show_msg
    ; patch the wave number and quota into the show_msg
    ld a,(wave)
    add a,'1'
    ld (tick_buf+5),a
    ld a,(quota_left)
    ld hl,tick_buf+17
    jp dec2

do_play:
    call update_player
    call update_robot
    call update_items
    call update_bolts
    call update_poofs
    call update_obstacles
    jp beat_step

; ---- wave cleared: card, then the next wave / episode
do_clear:
    call update_player
    call update_robot
    call update_poofs
    call update_bolts
    ld hl,state_timer
    dec (hl)
    ret nz
    call ov_close
    ld a,(wave)
    inc a
    cp 3
    jr z,sc_ep
    ld (wave),a
    call wave_setup
    ld a,SNG_EP
    call play_song
    ld a,ST_INTRO
    ld (state),a
    ld a,1
    ld (state_timer),a
    ret
sc_ep:
    xor a
    ld (wave),a
    ld a,(episode)
    inc a
    cp NUM_EPS
    jr z,sc_win
    ld (episode),a
    call wait_ov_gone
    jp episode_start
sc_win:
    call wait_ov_gone
    ld a,ST_WIN
    ld (state),a
    ld a,SNG_MENU
    call play_song
    ld hl,card_win
    jp ov_open

; let the closing overlay finish in both buffers
wait_ov_gone:
    ld a,(ov_on)
    or a
    ret z
    call begin_frame
    call draw_world
    call ov_step
    call hud_step
    call end_frame
    jr wait_ov_gone

; ---- a life was lost
do_lost:
    call update_poofs
    call update_player
    ld hl,state_timer
    dec (hl)
    ret nz
    ld a,(lives)
    or a
    jr z,sl_over
    ld a,ST_PLAY
    ld (state),a
    ld a,SNG_EP
    jp play_song
sl_over:
    ld a,ST_OVER
    ld (state),a
    ld a,50
    ld (state_timer),a
    ld a,SNG_OVER
    call play_song
    call ov_wait_free
    ld hl,card_over
    jp ov_open

do_over:
    call update_poofs
    ld hl,state_timer
    ld a,(hl)
    or a
    jr z,so_wait
    dec (hl)
    ret
so_wait:
    ld a,(inp_new)
    and IN_FIRE
    ret z
    ld a,1
    ld (quit_flag),a
    ret

do_win:
    call update_player
    call update_robot
    ld a,(inp_new)
    and IN_FIRE
    ret z
    call ov_close
    call wait_ov_gone
    ld hl,loop_n
    inc (hl)
    xor a
    ld (episode),a
    ld (wave),a
    jp episode_start

; close any overlay (the pop-up) synchronously so a card can open
ov_wait_free:
    ld a,(ov_on)
    or a
    ret z
    xor a
    ld (popup_on),a
    call ov_close
    jp wait_ov_gone

; ----------------------------------------------------------------------------
; player
; ----------------------------------------------------------------------------
update_player:
    ; the deepfake swapped left and right?
    ld hl,player_rev
    ld a,(hl)
    or a
    ld a,(inp)
    jr z,up_norev
    dec (hl)
    ld c,a
    and #FC
    bit 0,c
    jr z,up_rv1
    or IN_RIGHT
up_rv1:
    bit 1,c
    jr z,up_norev
    or IN_LEFT
up_norev:
    ld (pinp),a
    ld hl,player_cool
    ld a,(hl)
    or a
    jr z,up_c
    dec (hl)
up_c:
    ld hl,player_zap
    ld a,(hl)
    or a
    jr z,up_z
    dec (hl)
up_z:
    ld hl,player_slow
    ld a,(hl)
    or a
    jr z,up_fast
    dec (hl)
    ld a,(frame_ctr)
    and 2
    jr nz,up_fire           ; slowed: move every other frame
    ld c,1
    jr up_move
up_fast:
    ld c,1
    ld a,(player_hold)
    cp 5
    jr c,up_move
    ld c,2
up_move:
    ld a,(pinp)
    and IN_LEFT
    jr z,up_r
    ld a,(player_x)
    sub c
    jr nc,up_l1
    xor a
up_l1:
    ld (player_x),a
    ld a,1
    ld (player_dir),a
    jr up_held
up_r:
    ld a,(pinp)
    and IN_RIGHT
    jr z,up_still
    ld a,(player_x)
    add a,c
    cp 80-PLAYER_W+1
    jr c,up_r1
    ld a,80-PLAYER_W
up_r1:
    ld (player_x),a
    xor a
    ld (player_dir),a
up_held:
    ld hl,player_hold
    inc (hl)
    jr nz,up_fire
    dec (hl)
    jr up_fire
up_still:
    xor a
    ld (player_hold),a
up_fire:
    ld a,(state)
    cp ST_PLAY
    ret nz
    ld a,(inp)
    and IN_FIRE
    ret z
    ld a,(player_cool)
    or a
    ret nz
    ; free bolt?
    ld hl,bolts
    ld b,MAX_BOLTS
uf_lp:
    inc hl
    ld a,(hl)
    or a
    jr z,uf_free
    inc hl
    djnz uf_lp
    ret
uf_free:
    dec hl
    ld a,(player_x)
    add a,2
    ld (hl),a
    inc hl
    ld (hl),BOLT_Y
    ld a,(cool_max)
    ld (player_cool),a
    ld a,4
    ld (player_zap),a
    ld a,SFX_ZAP
    jp play_sfx

; ----------------------------------------------------------------------------
; the SlopBot: wanders along the top and prints slop
; ----------------------------------------------------------------------------
update_robot:
    ld a,(robot_print)
    or a
    jr z,ur_0
    dec a
    ld (robot_print),a
ur_0:
    ld hl,robot_flash
    ld a,(hl)
    or a
    jr z,ur_0b
    dec (hl)
ur_0b:
    ld a,(boss_on)
    or a
    call nz,robot_step
    call robot_step
    jr ur_2

robot_step:
    ld a,(robot_x)
    ld hl,robot_dx
    add a,(hl)
    ld (robot_x),a
    or a
    jr z,ur_flip
    cp 80-8
    jr nc,ur_flip
    call rand
    cp 5
    ret nc
ur_flip:
    ld a,(hl)
    neg
    ld (hl),a
    ret
ur_2:
    ld a,(state)
    cp ST_PLAY
    ret nz
    ld hl,spawn_timer
    dec (hl)
    ret nz
    ld b,8
    call rand_mod
    ld hl,spawn_int
    add a,(hl)
    ld (spawn_timer),a
    jp spawn_item

spawn_item:
    ; count active items, find a free slot
    ld ix,items
    ld b,MAX_ITEMS
    ld c,0
    ld hl,0
si_lp:
    ld a,(ix+IT_ON)
    or a
    jr z,si_free
    inc c
    jr si_next
si_free:
    ld a,h
    or l
    jr nz,si_next
    push ix
    pop hl
si_next:
    ld de,IT_SIZE
    add ix,de
    djnz si_lp
    ld a,h
    or l
    ret z
    ld a,(item_cap)
    cp c
    ret z
    ret c
    push hl
    pop ix
    ; kind: 3 = coffee, 4 = heart, else 0-2
    call rand
    cp 5
    ld c,3
    jr c,si_kind
    cp 8
    ld c,4
    jr c,si_kind
    ld a,(ep_mech)
    and MC_DECOY_REV|MC_DECOY_MISS
    jr z,si_slop
    call rand
    cp 40
    ld c,K_DECOY
    jr c,si_kind
si_slop:
    ld b,3
    call rand_mod
    ld c,a
si_kind:
    ld (ix+IT_KIND),c
    ld (ix+IT_ON),1
    ld (ix+IT_ANIM),0
    ld (ix+IT_T),0
    ld (ix+IT_YF),0
    ld (ix+IT_Y),SPAWN_Y
    call item_sprite
    ex de,hl
    ld a,(hl)               ; w + dx
    inc hl
    inc hl
    add a,(hl)
    ld (ix+IT_W),a
    ld b,a
    dec hl
    ld a,(hl)               ; h + dy
    inc hl
    inc hl
    add a,(hl)
    ld (ix+IT_H),a
    ; x = robot_x + (8 - w) / 2
    ld a,8
    sub b
    sra a
    ld hl,robot_x
    add a,(hl)
    ld (ix+IT_X),a
    call rand
    and 1
    add a,a
    dec a
    ld (ix+IT_DX),a
    ld a,6
    ld (robot_print),a
    ret

; IX = item -> DE = current sprite
item_sprite:
    ld a,(ix+IT_KIND)
    cp K_DECOY
    jr z,is_decoy
    cp 3
    jr c,is_slop
    sub 3
    add a,a
    add a,SS_POWER
    jp spr_get
is_slop:
    add a,a
    add a,a
    ld b,a
    ld a,(ix+IT_T)
    and 8
    rrca
    rrca
    add a,b
    add a,SS_ITEMS
    jp spr_get
is_decoy:
    ld a,(ix+IT_T)
    and 8
    rrca
    rrca
    add a,SS_DECOY
    jp spr_get

; ----------------------------------------------------------------------------
; items fall
; ----------------------------------------------------------------------------
update_items:
    ld ix,items
    ld b,MAX_ITEMS
ui_lp:
    push bc
    ld a,(ix+IT_ON)
    or a
    call nz,item_tick
    pop bc
    ld de,IT_SIZE
    add ix,de
    djnz ui_lp
    ret

item_tick:
    inc (ix+IT_T)
    ld hl,(fall_spd)
    ld a,(ix+IT_KIND)
    cp 2
    jr nz,it_1
    ; fast: 1.5x
    ld d,h
    ld e,l
    srl d
    rr e
    add hl,de
    jr it_move
it_1:
    cp 3
    jr c,it_move
    cp K_DECOY
    jr z,it_move
    ld hl,#00C0             ; power-ups drift down slowly
it_move:
    ld a,(drop_timer)
    or a
    jr z,it_mv2
    add hl,hl               ; the bass dropped
it_mv2:
    ld a,(ix+IT_YF)
    add a,l
    ld (ix+IT_YF),a
    ld a,(ix+IT_Y)
    adc a,h
    ld (ix+IT_Y),a
    ; zig-zag
    ld a,(ix+IT_KIND)
    cp 1
    jr nz,it_land
    ld a,(ix+IT_T)
    and 3
    jr nz,it_land
    ld a,(ix+IT_X)
    add a,(ix+IT_DX)
    jp m,it_bounce
    ld c,a
    add a,(ix+IT_W)
    cp 81
    jr nc,it_bounce
    ld (ix+IT_X),c
    jr it_land
it_bounce:
    ld a,(ix+IT_DX)
    neg
    ld (ix+IT_DX),a
it_land:
    ld a,(ix+IT_Y)
    add a,(ix+IT_H)
    cp SHELF_Y
    ret c
    ; it reached the shelf
    ld (ix+IT_ON),0
    ld a,(ix+IT_KIND)
    cp 3
    ret nc                  ; power-ups and decoys just fall away
    call add_miss
    ret c                   ; that cost a life (and said so)
    ld a,EH_MISS
    jp ep_msg

; one more slop on the shelf -> carry if that cost a life
add_miss:
    ld a,SFX_SOLD
    call play_sfx
    xor a
    ld (streak),a
    inc a
    ld (mult),a
    ld a,8
    ld (shelf_flash),a
    ld hl,misses
    inc (hl)
    ld a,HF_SHELF
    call hud_mark
    ld a,(misses)
    ld hl,miss_limit
    cp (hl)
    ccf
    ret nc
    call life_lost
    scf
    ret

life_lost:
    xor a
    ld (misses),a
    ld (drop_timer),a
    ld hl,lives
    dec (hl)
    ld a,HF_LIVES|HF_SHELF
    call hud_mark
    call kill_all_items
    xor a
    ld (popup_on),a
    ld (ban_on),a
    call ov_close
    ld a,SNG_LOST
    call play_song
    ld a,20
    ld (life_flash),a
    ld a,ST_LOST
    ld (state),a
    ld a,60
    ld (state_timer),a
    ld a,(lives)
    or a
    ld hl,msg_life_lost
    jr nz,ll_1
    ld hl,msg_no_lives
ll_1:
    jp show_msg

; poof every item (no points)
kill_all_items:
    push ix                 ; callers may be walking the items with IX
    ld ix,items
    ld b,MAX_ITEMS
ka_lp:
    ld a,(ix+IT_ON)
    or a
    jr z,ka_next
    ld (ix+IT_ON),0
    push bc
    ld b,(ix+IT_X)
    ld c,(ix+IT_Y)
    call add_poof
    pop bc
ka_next:
    ld de,IT_SIZE
    add ix,de
    djnz ka_lp
    pop ix
    ret

; ----------------------------------------------------------------------------
; zaps
; ----------------------------------------------------------------------------
update_bolts:
    ld hl,bolts
    ld b,MAX_BOLTS
ub_lp:
    push bc
    push hl
    inc hl
    ld a,(hl)
    or a
    jr z,ub_next
    sub BOLT_SPEED
    cp PLAY_TOP+2
    jr nc,ub_1
    xor a
ub_1:
    ld (hl),a
    or a
    jr z,ub_next
    dec hl
    ld (bolt_cur),hl
    ld b,(hl)
    ld c,a
    call bolt_hits
ub_next:
    pop hl
    inc hl
    inc hl
    pop bc
    djnz ub_lp
    ret

; B = bolt x, C = bolt y. Checks everything the bolt can hit.
bolt_hits:
    ; obstacles first: they absorb the zap
    call bolt_vs_obstacles
    ret c
    ld a,(boss_on)
    or a
    call nz,bolt_vs_boss
    ret c
    ld ix,items
    ld e,MAX_ITEMS
bh_lp:
    ld a,(ix+IT_ON)
    or a
    jr z,bh_next
    ; item.x < bx+BOLT_W
    ld a,b
    add a,BOLT_W
    ld d,a
    ld a,(ix+IT_X)
    cp d
    jr nc,bh_next
    ; item.x + w > bx
    add a,(ix+IT_W)
    dec a
    cp b
    jr c,bh_next
    ; item.y < by + BOLT_H
    ld a,c
    add a,BOLT_H
    ld d,a
    ld a,(ix+IT_Y)
    cp d
    jr nc,bh_next
    add a,(ix+IT_H)
    dec a
    cp c
    jr c,bh_next
    call bolt_kill
    jp zap_item
bh_next:
    push de
    ld de,IT_SIZE
    add ix,de
    pop de
    dec e
    jr nz,bh_lp
    ret

bolt_kill:
    ld hl,(bolt_cur)
    inc hl
    ld (hl),0
    ret

; IX = item hit by a zap
zap_item:
    ld (ix+IT_ON),0
    ld b,(ix+IT_X)
    ld c,(ix+IT_Y)
    call add_poof
    ld a,(ix+IT_KIND)
    cp K_DECOY
    jp z,zi_decoy
    cp 3
    jr z,zi_coffee
    jp nc,zi_heart
    ; slop: points by kind
    ld e,a
    ld d,0
    ld hl,kind_points
    add hl,de
    ld a,(hl)
    call add_score
    ld a,SFX_BOOM
    call play_sfx
    ; streak / multiplier
    ld hl,streak
    inc (hl)
    ld a,(hl)
    cp 6
    jr c,zi_q
    ld (hl),0
    ld a,(mult)
    cp 4
    jr nc,zi_q
    inc a
    ld (mult),a
    ld hl,msg_streak
    call show_msg
    ld a,(mult)
    add a,'0'
    ld (tick_buf+14),a
    jr zi_q2
zi_q:
    call rand
    cp 70
    jr nc,zi_q2
    ld a,EH_KILL
    call ep_msg
zi_q2:
    ld a,(boss_on)
    or a
    ret nz                  ; while the boss fights, only hits on it count
    call try_split
    ret c
    ld hl,quota_left
    dec (hl)
    ld a,HF_INFO
    call hud_mark
    ld a,(quota_left)
    or a
    ret nz
    jp quota_done

zi_coffee:
    ld a,SFX_POWER
    call play_sfx
    ld hl,msg_coffee
    call show_msg
    ; every slop on screen counts as zapped
    ld ix,items
    ld b,MAX_ITEMS
zc_lp:
    push bc
    ld a,(ix+IT_ON)
    or a
    jr z,zc_next
    ld a,(ix+IT_KIND)
    cp 3
    jr nc,zc_next
    ld (ix+IT_ON),0
    ld b,(ix+IT_X)
    ld c,(ix+IT_Y)
    call add_poof
    ld a,#10
    call add_score
    ld a,(boss_on)
    or a
    jr nz,zc_next
    ld hl,quota_left
    ld a,(hl)
    or a
    jr z,zc_next
    dec (hl)
zc_next:
    ld de,IT_SIZE
    add ix,de
    pop bc
    djnz zc_lp
    ld a,HF_INFO
    call hud_mark
    ld a,(boss_on)
    or a
    ret nz
    ld a,(quota_left)
    or a
    ret nz
    jp quota_done

zi_heart:
    ld a,SFX_POWER
    call play_sfx
    ld hl,lives
    ld a,(hl)
    cp 6
    jr nc,zh_1
    inc (hl)
zh_1:
    ld a,HF_LIVES
    call hud_mark
    ld hl,msg_heart
    jp show_msg

; ---- the zapped thing was a decoy: a deepfake of Themis or a real human
zi_decoy:
    ld a,SFX_THUD
    call play_sfx
    xor a
    ld (streak),a
    inc a
    ld (mult),a
    ld a,(ep_mech)
    and MC_DECOY_MISS
    jr z,zd_rev
    call add_miss           ; zapping a human counts as slop on the shelf
    ret c
    ld a,EH_DECOY
    jp ep_msg
zd_rev:
    ld a,REV_TIME
    ld (player_rev),a
    ld a,EH_DECOY
    jp ep_msg

; ---- IX = slop just zapped: maybe it splits in two -> carry (doesn't count)
try_split:
    ld a,(ep_mech)
    and MC_SPLIT
    ret z
    bit 0,(ix+IT_ANIM)
    ret nz                  ; the halves don't split again (carry is clear)
    call rand
    cp 128
    ccf
    ret nc
    ; a free slot besides this one
    ld (ix+IT_ON),1
    ld iy,items
    ld b,MAX_ITEMS
ts_lp:
    ld a,(iy+IT_ON)
    or a
    jr z,ts_free
    ld de,IT_SIZE
    add iy,de
    djnz ts_lp
    ld (ix+IT_ON),0
    or a
    ret
ts_free:
    ld a,(ix+IT_KIND)
    ld (iy+IT_KIND),a
    ld a,(ix+IT_W)
    ld (iy+IT_W),a
    ld a,(ix+IT_H)
    ld (iy+IT_H),a
    ld a,(ix+IT_Y)
    ld (iy+IT_Y),a
    ld a,(ix+IT_YF)
    ld (iy+IT_YF),a
    ld (iy+IT_ON),1
    ld (iy+IT_ANIM),1
    ld (ix+IT_ANIM),1
    ld (iy+IT_T),4
    ld (ix+IT_T),0
    ld (iy+IT_DX),1
    ld (ix+IT_DX),-1
    ; spread them apart: left half x-3 (min 0), right half x+3 (fits)
    ld a,(ix+IT_X)
    ld c,a
    sub 3
    jr nc,ts_l
    xor a
ts_l:
    ld (ix+IT_X),a
    ld a,c
    add a,3
    ld c,a
    add a,(iy+IT_W)
    cp 81
    jr c,ts_r
    ld a,80
    sub (iy+IT_W)
    ld c,a
ts_r:
    ld (iy+IT_X),c
    ld a,SFX_POP
    call play_sfx
    ld a,EH_SPECIAL
    call ep_msg
    scf
    ret

; ---- the quota is done: the wave is cleared, or the boss wakes up
quota_done:
    ld a,(ep_mech)
    and MC_BOSS
    jp z,wave_clear
    ld a,(wave)
    cp 2
    jp nz,wave_clear
    ld a,1
    ld (boss_on),a
    ld a,BOSS_HP
    ld (quota_left),a
    ld a,HF_INFO
    call hud_mark
    ld a,SFX_POPUP
    call play_sfx
    ld a,EH_SPECIAL
    jp ep_msg

; B = bolt x, C = bolt y -> carry if the bolt hit the SlopBot
bolt_vs_boss:
    ld a,c
    cp ROBOT_Y+20
    jr nc,bvs_no
    ld a,(robot_x)
    ld d,a
    ld a,b
    add a,BOLT_W
    sub d
    jr c,bvs_no
    jr z,bvs_no
    cp 8+BOLT_W
    jr nc,bvs_no
    call bolt_kill
    ld a,SFX_THUD
    call play_sfx
    ld a,8
    ld (robot_flash),a
    ld a,#50
    call add_score
    ld hl,quota_left
    dec (hl)
    ld a,HF_INFO
    call hud_mark
    ld a,(quota_left)
    or a
    jr nz,bvs_hit
    ; down it goes
    xor a
    ld (boss_on),a
    ld a,(robot_x)
    ld b,a
    ld c,ROBOT_Y
    call add_poof
    ld a,(robot_x)
    add a,4
    ld b,a
    ld c,ROBOT_Y+8
    call add_poof
    call wave_clear
    ld a,EH_BOSS
    call ep_msg
bvs_hit:
    scf
    ret
bvs_no:
    or a
    ret

; ---- every so often the bass drops (episode mechanic)
beat_step:
    ld a,(ep_mech)
    and MC_BEAT
    ret z
    ld hl,drop_timer
    ld a,(hl)
    or a
    jr z,bs_wait
    dec (hl)
    ret
bs_wait:
    ld hl,beat_timer
    dec (hl)
    ret nz
    ld (hl),BEAT_EVERY
    ld a,DROP_TIME
    ld (drop_timer),a
    ld a,SFX_POWER
    call play_sfx
    ld a,EH_SPECIAL
    jp ep_msg

wave_clear:
    call kill_all_items
    xor a
    ld (popup_on),a
    ld (ban_on),a
    ld (drop_timer),a
    ld (player_rev),a
    ld (boss_on),a
    call ov_wait_free
    ; bonus: 100 per wave number
    ld a,(wave)
    inc a
    call add_score100
    ld a,SNG_CLEAR
    call play_song
    ld a,ST_CLEAR
    ld (state),a
    ld a,90
    ld (state_timer),a
    ld hl,msgs_clear
    call show_msg_rand
    ld hl,card_clear
    jp ov_open

; ----------------------------------------------------------------------------
; poofs
; ----------------------------------------------------------------------------
; B = x, C = y
add_poof:
    push hl
    ld hl,poofs
    ld d,MAX_POOFS
ap_lp:
    inc hl
    ld a,(hl)
    or a
    jr z,ap_free
    inc hl
    inc hl
    inc hl
    dec d
    jr nz,ap_lp
    pop hl
    ret
ap_free:
    dec hl
    ld (hl),b
    inc hl
    ld a,c
    or a
    jr nz,ap_1
    inc a
ap_1:
    ld (hl),a
    inc hl
    ld (hl),0               ; frame
    inc hl
    ld (hl),2               ; timer
    pop hl
    ret

update_poofs:
    ld hl,poofs
    ld b,MAX_POOFS
upf_lp:
    inc hl
    ld a,(hl)
    or a
    jr z,upf_skip
    inc hl
    inc hl
    dec (hl)
    jr nz,upf_next
    ld (hl),2
    dec hl
    inc (hl)
    ld a,(hl)
    inc hl
    cp 3
    jr c,upf_next
    dec hl
    dec hl
    ld (hl),0               ; y = 0: free
    inc hl
    inc hl
upf_next:
    inc hl
    djnz upf_lp
    ret
upf_skip:
    inc hl
    inc hl
    inc hl
    djnz upf_lp
    ret

; ----------------------------------------------------------------------------
; drawing
; ----------------------------------------------------------------------------
draw_world:
    ; robot (blinks when the boss is hit)
    ld a,(robot_flash)
    and 2
    jr nz,dw_items
    ld a,(robot_print)
    or a
    ld a,SS_ROBOT
    jr z,dw_r1
    ld a,SS_ROBOT+2
dw_r1:
    call spr_get
    ld a,(robot_x)
    ld b,a
    ld c,ROBOT_Y
    call draw_masked
dw_items:
    ld ix,items
    ld b,MAX_ITEMS
dw_it:
    push bc
    ld a,(ix+IT_ON)
    or a
    jr z,dw_itn
    call item_sprite
    ld b,(ix+IT_X)
    ld c,(ix+IT_Y)
    call draw_masked
dw_itn:
    ld de,IT_SIZE
    add ix,de
    pop bc
    djnz dw_it
    call draw_obstacles
    ; bolts
    ld hl,bolts
    ld b,MAX_BOLTS
dw_b:
    push bc
    ld a,(hl)
    inc hl
    ld c,(hl)
    inc hl
    push hl
    ld b,a
    ld a,c
    or a
    jr z,dw_bn
    push bc
    ld a,SS_BOLT
    call spr_get
    pop bc
    call draw_masked
dw_bn:
    pop hl
    pop bc
    djnz dw_b
    ; poofs
    ld hl,poofs
    ld b,MAX_POOFS
dw_p:
    push bc
    ld a,(hl)
    inc hl
    ld c,(hl)
    inc hl
    ld b,a
    ld a,(hl)
    inc hl
    inc hl
    push hl
    ld e,a
    ld a,c
    or a
    jr z,dw_pn
    ld a,e
    add a,a
    add a,SS_POOF
    push bc
    call spr_get
    pop bc
    call draw_masked
dw_pn:
    pop hl
    pop bc
    djnz dw_p
    ; Themis
    ld a,(player_zap)
    or a
    ld a,SS_PLAYER+6
    jr nz,dw_pl
    ld a,(player_slow)
    ld hl,player_rev
    or (hl)
    jr z,dw_p2
    ld a,(frame_ctr)
    and 8
    ld a,SS_PLAYER+8
    jr nz,dw_pl
dw_p2:
    ld a,(player_hold)
    or a
    ld a,SS_PLAYER
    jr z,dw_pl
    ld a,(frame_ctr)
    and 4
    ld a,SS_PLAYER+2
    jr z,dw_pl
    ld a,SS_PLAYER+4
dw_pl:
    call spr_get
    ld a,(player_x)
    ld b,a
    ld c,PLAYER_Y
    jp draw_masked

; ----------------------------------------------------------------------------
; palette flashes: shelf (an item was sold) and the whole field (life lost)
; ----------------------------------------------------------------------------
flash_step:
    ld hl,(ep_raster)
    ld de,4
    add hl,de               ; zone 2 entry (playfield)
    ld e,(hl)
    inc hl
    ld d,(hl)
    inc de
    inc de                  ; pen 0 colour
    ld a,(life_flash)
    or a
    jr z,fs_shelf
    dec a
    ld (life_flash),a
    and 2
    ld a,#4C                ; bright red
    jr nz,fs_set
    ld a,(ep_pen0)
fs_set:
    ld (de),a
    ret
fs_shelf:
    ld a,(drop_timer)
    or a
    jr z,fs_p0
    ld a,(frame_ctr)
    and 4
    ld a,#4D                ; bright magenta strobe
    jr nz,fs_p1
fs_p0:
    ld a,(ep_pen0)
fs_p1:
    ld (de),a
    ; shelf zone (entry 5)
    ld hl,(ep_raster)
    ld de,10
    add hl,de
    ld e,(hl)
    inc hl
    ld d,(hl)
    ld a,d
    or e
    ret z
    inc de
    inc de
    inc de                  ; pen 1 of the shelf
    ld a,(shelf_flash)
    or a
    jr z,fs_off
    dec a
    ld (shelf_flash),a
    and 2
    ld a,#4C
    jr nz,fs_s2
fs_off:
    ld a,(ep_shelf1)
fs_s2:
    ld (de),a
    ret
