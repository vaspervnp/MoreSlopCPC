; ============================================================================
; AY music + sound effect player. Called at 50 Hz from the interrupt.
; Data format: see tools/music.py.  Channel C is shared with the effects.
; ============================================================================

CH_ORD   equ 0          ; word: next order entry
CH_PAT   equ 2          ; word: pattern pointer
CH_TR    equ 4          ; transpose
CH_WAIT  equ 5          ; frames until the next event
CH_LEN   equ 6          ; note length in frames
CH_NOTE  equ 7
CH_INST  equ 8          ; word: instrument
CH_STEP  equ 10
CH_ON    equ 11
CH_VOL   equ 12         ; out: volume
CH_MIX   equ 13         ; out: bit0 tone, bit1 noise
CH_NP    equ 14         ; out: noise period
CH_PER   equ 15         ; out: word period
CH_SIZE  equ 17

; A = song number -> request (picked up at the next tick)
play_song:
    inc a
    ld (song_req),a
    ret

stop_music:
    ld a,#FF
    ld (song_req),a
    ret

; A = effect number (1..)
play_sfx:
    ld (sfx_req),a
    ret

music_tick:
    ld a,(song_req)
    or a
    jr z,mt_run
    ld b,a
    xor a
    ld (song_req),a
    ld a,b
    cp #FF
    jr nz,mt_start
    xor a
    ld (ch_a+CH_ON),a
    ld (ch_b+CH_ON),a
    ld (ch_c+CH_ON),a
    jr mt_run
mt_start:
    dec a
    call mus_start
mt_run:
    ld ix,ch_a
    call ch_tick
    ld ix,ch_b
    call ch_tick
    ld ix,ch_c
    call ch_tick
    call sfx_tick
    ; ---- build the AY registers
    ld hl,(ch_a+CH_PER)
    ld (ay_regs+0),hl
    ld hl,(ch_b+CH_PER)
    ld (ay_regs+2),hl
    ld hl,(ch_c+CH_PER)
    ld (ay_regs+4),hl
    ld a,(ch_a+CH_VOL)
    ld (ay_regs+8),a
    ld a,(ch_b+CH_VOL)
    ld (ay_regs+9),a
    ld a,(ch_c+CH_VOL)
    ld (ay_regs+10),a
    ; mixer: start with everything off, enable what is used
    ld c,#3F
    ld a,(ch_a+CH_MIX)
    rra
    jr nc,mx1
    res 0,c
mx1:
    rra
    jr nc,mx2
    res 3,c
    ld a,(ch_a+CH_NP)
    ld (ay_regs+6),a
mx2:
    ld a,(ch_b+CH_MIX)
    rra
    jr nc,mx3
    res 1,c
mx3:
    rra
    jr nc,mx4
    res 4,c
    ld a,(ch_b+CH_NP)
    ld (ay_regs+6),a
mx4:
    ld a,(ch_c+CH_MIX)
    rra
    jr nc,mx5
    res 2,c
mx5:
    rra
    jr nc,mx6
    res 5,c
    ld a,(ch_c+CH_NP)
    ld (ay_regs+6),a
mx6:
    ld a,c
    ld (ay_regs+7),a
    ; ---- write registers 0-10
    ld hl,ay_regs
    ld de,ay_last
    ld c,0
aw_lp:
    ld a,(de)
    cp (hl)
    jr z,aw_same
    ld a,(hl)
    ld (de),a
    push de
    ld e,c
    call ay_out
    pop de
aw_same:
    inc hl
    inc de
    inc c
    ld a,c
    cp 11
    jr nz,aw_lp
    ret

; E = register, (HL) = value
ay_out:
    push bc
    ld b,#F4
    out (c),e
    ld bc,#F6C0
    out (c),c
    ld bc,#F600
    out (c),c
    ld b,#F4
    ld a,(hl)
    out (c),a
    ld bc,#F680
    out (c),c
    ld bc,#F600
    out (c),c
    pop bc
    ret

; A = song index
mus_start:
    add a,a
    ld l,a
    ld h,0
    ld de,mus_songs
    add hl,de
    ld e,(hl)
    inc hl
    ld d,(hl)
    ld a,(de)
    ld (mus_speed),a
    inc de
    ld ix,ch_a
    call ch_init
    ld ix,ch_b
    call ch_init
    ld ix,ch_c
    ; fall through
ch_init:
    ld a,(de)
    ld (ix+CH_ORD),a
    inc de
    ld a,(de)
    ld (ix+CH_ORD+1),a
    inc de
    push de
    call ch_load_order
    ld (ix+CH_WAIT),1
    ld a,(mus_speed)
    ld (ix+CH_LEN),a
    ld hl,inst_silent
    ld (ix+CH_INST),l
    ld (ix+CH_INST+1),h
    ld (ix+CH_STEP),0
    pop de
    ret

; load the pattern of the next order entry (handles end / loop)
ch_load_order:
    ld l,(ix+CH_ORD)
    ld h,(ix+CH_ORD+1)
clo_again:
    ld e,(hl)
    inc hl
    ld d,(hl)
    inc hl
    ld a,d
    or e
    jr nz,clo_ok
    ld e,(hl)
    inc hl
    ld d,(hl)
    ld a,d
    or e
    jr z,clo_stop
    ex de,hl
    jr clo_again
clo_ok:
    ld a,(hl)
    inc hl
    ld (ix+CH_TR),a
    ld (ix+CH_PAT),e
    ld (ix+CH_PAT+1),d
    ld (ix+CH_ORD),l
    ld (ix+CH_ORD+1),h
    ld (ix+CH_ON),1
    ret
clo_stop:
    ld (ix+CH_ON),0
    ld (ix+CH_VOL),0
    ld (ix+CH_MIX),0
    ret

ch_tick:
    ld a,(ix+CH_ON)
    or a
    jr nz,ct_on
    ld (ix+CH_VOL),a
    ld (ix+CH_MIX),a
    ret
ct_on:
    dec (ix+CH_WAIT)
    jr nz,ct_inst
    ld l,(ix+CH_PAT)
    ld h,(ix+CH_PAT+1)
ct_read:
    ld a,(hl)
    inc hl
    cp #FF
    jr nz,ct_n1
    call ch_load_order
    ld a,(ix+CH_ON)
    or a
    ret z
    ld l,(ix+CH_PAT)
    ld h,(ix+CH_PAT+1)
    jr ct_read
ct_n1:
    cp #60
    jr nc,ct_n2
    add a,(ix+CH_TR)
    ld (ix+CH_NOTE),a
    ld (ix+CH_STEP),0
    jr ct_wait
ct_n2:
    cp #80
    jr nc,ct_n3
    sub #5F
    ld b,a
    ld a,(mus_speed)
    ld c,a
    xor a
ct_mul:
    add a,c
    djnz ct_mul
    ld (ix+CH_LEN),a
    jr ct_read
ct_n3:
    cp #C0
    jr nc,ct_n4
    sub #80
    add a,a
    push hl
    ld l,a
    ld h,0
    ld de,mus_insts
    add hl,de
    ld e,(hl)
    inc hl
    ld d,(hl)
    ld (ix+CH_INST),e
    ld (ix+CH_INST+1),d
    pop hl
    jr ct_read
ct_n4:
    jr nz,ct_wait           ; #C1 hold (flags from cp #C0)
    ld de,inst_silent
    ld (ix+CH_INST),e
    ld (ix+CH_INST+1),d
    ld (ix+CH_STEP),0
ct_wait:
    ld a,(ix+CH_LEN)
    ld (ix+CH_WAIT),a
    ld (ix+CH_PAT),l
    ld (ix+CH_PAT+1),h
ct_inst:
    ld l,(ix+CH_INST)
    ld h,(ix+CH_INST+1)
    ld a,(ix+CH_STEP)
    add a,a
    ld e,a
    ld d,0
    add hl,de
    ld a,(hl)
    cp #FF
    jr nz,ci_ok
    inc hl
    ld a,(hl)
    ld (ix+CH_STEP),a
    jr ct_inst
ci_ok:
    inc (ix+CH_STEP)
    ld c,a
    and #0F
    ld (ix+CH_VOL),a
    inc hl
    ld b,(hl)
    bit 4,c
    jr z,ci_tone
    ld (ix+CH_NP),b
    ld (ix+CH_MIX),2
    ret
ci_tone:
    ld (ix+CH_MIX),1
    ld a,(ix+CH_NOTE)
    add a,b
    cp 96
    jr c,ci_inr
    bit 7,b
    ld a,0
    jr nz,ci_inr
    ld a,95
ci_inr:
    add a,a
    ld e,a
    ld d,0
    ld hl,mus_periods
    add hl,de
    ld a,(hl)
    ld (ix+CH_PER),a
    inc hl
    ld a,(hl)
    ld (ix+CH_PER+1),a
    ret

; ----------------------------------------------------------------------------
; sound effects on channel C: frames of (ctl, period lo, period hi, noise)
; ctl bits 0-3 volume, bit 4 noise on, bit 5 tone off; #FF ends
; ----------------------------------------------------------------------------
sfx_tick:
    ld a,(sfx_req)
    or a
    jr z,st_run
    ld b,a
    xor a
    ld (sfx_req),a
    ld a,b
    dec a
    add a,a
    ld l,a
    ld h,0
    ld de,sfx_tab
    add hl,de
    ld e,(hl)
    inc hl
    ld d,(hl)
    ld (sfx_ptr),de
st_run:
    ld hl,(sfx_ptr)
    ld a,h
    or l
    ret z
    ld a,(hl)
    cp #FF
    jr nz,st_frame
    ld hl,0
    ld (sfx_ptr),hl
    ret
st_frame:
    ld c,a
    and #0F
    ld (ch_c+CH_VOL),a
    inc hl
    ld e,(hl)
    inc hl
    ld d,(hl)
    inc hl
    ld (ch_c+CH_PER),de
    ld a,(hl)
    inc hl
    ld (ch_c+CH_NP),a
    ld (sfx_ptr),hl
    ld b,1
    bit 5,c
    jr z,st_t
    ld b,0
st_t:
    bit 4,c
    jr z,st_n
    set 1,b
st_n:
    ld a,b
    ld (ch_c+CH_MIX),a
    ret
