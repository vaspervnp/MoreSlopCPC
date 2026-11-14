; ============================================================================
; MORE SLOP - constants
; ============================================================================

; memory -----------------------------------------------------------------
STACK_TOP   equ #4000           ; stack grows down from the top of bank 0
CFG_BASE    equ #C0             ; RAM config: 64K base
SCR_C0      equ #C0             ; screen buffer at #C000
SCR_80      equ #80             ; screen buffer at #8000
BANK_WIN    equ #4000           ; where extra banks appear (configs #C4-#C7)
BG_BANK     equ #C4             ; bank holding the current episode's background
DIR_CFG     equ #C5             ; bank with the directory of packed data at #4000
EP_HI       equ #6800           ; the episode's HIGH blob (256-aligned)
LO_SLOT_SIZE equ 448            ; the episode's LOW blob (song, raster zones)

; LOW blob header (src: tools/episodes.py)
EL_RAST     equ 0               ; raster table (6 words)
EL_MODE     equ 12
EL_OBST     equ 13              ; OB_* mask
EL_MECH     equ 14              ; MC_* mask
EL_SONG     equ 16

; gate array values (ROMs off, no int reset)
GA_MODE0    equ #8C
GA_MODE1    equ #8D

; screen layout (lines) ----------------------------------------------------
HUD_ROW_SCORE equ 0
HUD_ROW_INFO  equ 8
HUD_ROW_TICK  equ 24
PLAY_TOP    equ 40              ; first playfield line
ROBOT_Y     equ 42
SPAWN_Y     equ 60
POPUP_MINY  equ 70
SHELF_Y     equ 190             ; items whose bottom reaches this are lost
PLAYER_Y    equ 164
PLAYER_W    equ 6
PLAYER_H    equ 24
BOLT_Y      equ 150
BOLT_W      equ 2
BOLT_H      equ 10
BOLT_SPEED  equ 9

; object limits -------------------------------------------------------------
MAX_ITEMS   equ 8
MAX_BOLTS   equ 2
MAX_POOFS   equ 6
MAX_BROS    equ 2

; item object (IX) ----------------------------------------------------------
IT_ON       equ 0               ; 0 free, else kind+1
IT_X        equ 1
IT_YF       equ 2               ; y fraction
IT_Y        equ 3
IT_DX       equ 4               ; zig-zag direction (+1 / -1)
IT_T        equ 5               ; timer
IT_W        equ 6
IT_H        equ 7
IT_KIND     equ 8
IT_ANIM     equ 9
IT_SIZE     equ 10

; sprite set (table of words) -----------------------------------------------
SS_PLAYER   equ 0               ; 5 frames: idle walk1 walk2 zap dizzy
SS_ROBOT    equ 10              ; 2 frames
SS_ITEMS    equ 14              ; 3 kinds x 2 frames
SS_POWER    equ 26              ; coffee, heart
SS_POOF     equ 30              ; 3 frames
SS_BOLT     equ 36              ; 1
SS_BRO      equ 38              ; float, walk1, walk2
SS_DECOY    equ 44              ; 2 frames

; item kinds
K_COFFEE    equ 3
K_HEART     equ 4
K_DECOY     equ 5

; game states -----------------------------------------------------------------
ST_INTRO    equ 0
ST_PLAY     equ 1
ST_CLEAR    equ 2
ST_LOST     equ 3
ST_OVER     equ 4
ST_WIN      equ 5
ST_PAUSE    equ 6

; keyboard matrix: (line, bit) ------------------------------------------------
KL_RIGHT    equ 0
KB_RIGHT    equ #02
KL_LEFT     equ 1
KB_LEFT     equ #01
KL_UP       equ 0
KB_UP       equ #01
KL_DOWN     equ 0
KB_DOWN     equ #04
KL_SPACE    equ 5
KB_SPACE    equ #80
KL_RETURN   equ 2
KB_RETURN   equ #04
KL_A        equ 8
KB_A        equ #20
KL_D        equ 7
KB_D        equ #20
KL_P        equ 3
KB_P        equ #08
KL_ESC      equ 8
KB_ESC      equ #04
KL_1        equ 8
KB_1        equ #01
KL_2        equ 8
KB_2        equ #02
KL_3        equ 7
KB_3        equ #02
KL_H        equ 5
KB_H        equ #10
KL_JOY      equ 9
KB_JUP      equ #01
KB_JDOWN    equ #02
KB_JLEFT    equ #04
KB_JRIGHT   equ #08
KB_JFIRE    equ #30

; sound effects -----------------------------------------------------------------
SFX_ZAP     equ 1
SFX_BOOM    equ 2
SFX_SOLD    equ 3
SFX_POPUP   equ 4
SFX_BLIP    equ 5
SFX_POWER   equ 6
SFX_THUD    equ 7
SFX_POP     equ 8
SFX_START   equ 9

; text control codes
TX_FG       equ 1
TX_BG       equ 2

; ---------------------------------------------------------------------------
; macros
; ---------------------------------------------------------------------------

; HL -> same x on the next screen line (works for #8000 and #C000 buffers)
macro NEXTLINE
    ld a,h
    add a,8
    ld h,a
    and #38
    jr nz,@nl
    ld a,l
    add a,#50
    ld l,a
    ld a,h
    adc a,#C0
    ld h,a
@nl
mend

; DE -> next screen line
macro NEXTLINE_DE
    ld a,d
    add a,8
    ld d,a
    and #38
    jr nz,@nl
    ld a,e
    add a,#50
    ld e,a
    ld a,d
    adc a,#C0
    ld d,a
@nl
mend

; Z set if the key IS pressed (matrix is active low): KEY line,mask
macro KEY line,mask
    ld a,(keymap+{line})
    and {mask}
mend
