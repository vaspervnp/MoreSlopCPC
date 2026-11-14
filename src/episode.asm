; ============================================================================
; Episodes: everything that differs between them is packed in banks #C5-#C7
; (tools/pack_banks.py) and unpacked when the episode starts:
;   background -> bank #C4 (for repairs) and both screens
;   HIGH blob  -> EP_HI   (sprite set, card, message tables, sprites, texts)
;   LOW blob   -> lo_slot (raster table, mode, obstacles, mechanics, song)
; The directory at #4000 of bank #C5 has 3 bytes per entry: bank, address.
; Entry 0 is the menu picture, then 3 per episode (background, HIGH, LOW).
; ============================================================================

; A = directory entry -> HL = packed stream, its bank paged in at #4000
dir_entry:
    ld l,a
    add a,a
    add a,l
    ld l,a
    ld h,BANK_WIN/256
    push hl
    ld a,DIR_CFG
    call set_cfg
    pop hl
    ld a,(hl)
    inc hl
    ld e,(hl)
    inc hl
    ld d,(hl)
    call set_cfg
    ex de,hl
    ret

; A = directory entry, DE = destination (not in #4000-#7FFF) -> DE = end
unpack_entry:
    push de
    call dir_entry
    pop de
    call lz2_unpack
    ld a,CFG_BASE
    jp set_cfg

; ----------------------------------------------------------------------------
; LZ2 unpacker (format: tools/cpcgfx.py). HL = source, DE = destination.
; Returns DE = end of the output.
; ----------------------------------------------------------------------------
lz2_unpack:
    ld a,(hl)
    inc hl
    cp #80
    jr nc,l2_match
    ld c,a                  ; a+1 literals
    ld b,0
    inc bc
    ldir
    jr lz2_unpack
l2_match:
    cp #C0
    jr nc,l2_long
    and #3F                 ; short: a+2 bytes from dst-(o+1)
    add a,2
    ld c,a
    ld b,0
    ld a,(hl)
    inc hl
    push hl
    cpl
    ld l,a
    ld h,#FF
    add hl,de
    ldir
    pop hl
    jr lz2_unpack
l2_long:
    ld c,(hl)               ; BC = offset
    inc hl
    ld b,(hl)
    inc hl
    cp #FF
    jr nz,l2_l1
    ld a,b
    or c
    ret z                   ; offset 0: the end
    ld a,(hl)               ; length - 66
    inc hl
    push hl
    push bc
    ld l,a
    ld h,0
    ld bc,66
    add hl,bc
    pop bc
    jr l2_copy
l2_l1:
    and #3F
    add a,3
    push hl
    ld l,a
    ld h,0
l2_copy:                    ; HL = length, BC = offset, (SP) = source
    push hl
    ld h,d
    ld l,e
    or a
    sbc hl,bc
    pop bc
    ldir
    pop hl
    jr lz2_unpack

; ----------------------------------------------------------------------------
; unpack episode (episode); the screen is blanked meanwhile
; ----------------------------------------------------------------------------
ep_load:
    call stop_music         ; the song lives in lo_slot
    ld hl,rast_black
    ld (raster_ptr),hl
    call wait_vbl
    call wait_vbl
    ld a,(episode)
    ld b,a
    add a,a
    add a,b
    ld (ep_dir),a           ; 3 * episode
    ; HIGH blob via the hidden screen
    add a,2
    ld de,#8000
    call unpack_entry
    ex de,hl
    ld de,#8000
    or a
    sbc hl,de
    ld b,h
    ld c,l
    ld hl,#8000
    ld de,EP_HI
    ldir
    ; LOW blob straight into place
    ld a,(ep_dir)
    add a,3
    ld de,lo_slot
    call unpack_entry
    ; background: #8000, then #C000 and bank #C4
    ld a,(ep_dir)
    inc a
    ld de,#8000
    call unpack_entry
    ld hl,#8000
    ld de,#C000
    ld bc,#4000
    ldir
    ld a,BG_BANK
    call set_cfg
    ld hl,#8000
    ld de,BANK_WIN
    ld bc,#4000
    ldir
    ld a,CFG_BASE
    call set_cfg
    ; what the episode is made of
    ld a,(lo_slot+EL_MODE)
    ld (cur_mode),a
    ld a,(lo_slot+EL_OBST)
    ld (ep_obst),a
    ld a,(lo_slot+EL_MECH)
    ld (ep_mech),a
    ld hl,lo_slot+EL_RAST
    ld (ep_raster),hl
    ld hl,EP_HI
    ld (cur_set),hl
    ld hl,(EP_HI+EH_CARD)
    ld (ep_card),hl
    ret

; A = EH_ offset -> HL = that pointer of the episode header (0 = none)
ep_ptr:
    ld l,a
    ld h,EP_HI/256
    ld a,(hl)
    inc hl
    ld h,(hl)
    ld l,a
    ret

; A = EH_ offset of a message table: show one of its messages at random
ep_msg:
    call ep_ptr
    ld a,h
    or l
    ret z
    jp show_msg_rand
