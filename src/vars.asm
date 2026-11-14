; ============================================================================
; variables (LOW, zero unless stated)
; ============================================================================

; aligned text tables: m1_tab at page offset 0, m0_tab at +16
    align 256
m1_tab:     defs 16,0
m0_tab:     defs 4,0

; interrupt / system
int_zone:   db 0
raster_ptr: dw rast_none
vbl_count:  db 0
frame_ctr:  db 0
cur_cfg:    db CFG_BASE
keymap:     defs 10,#FF

; music
song_req:   db 0
sfx_req:    db 0
sfx_ptr:    dw 0
mus_speed:  db 6
ch_a:       defs CH_SIZE,0
ch_b:       defs CH_SIZE,0
ch_c:       defs CH_SIZE,0
ay_regs:    defs 14,0

; video
draw_hi:    db SCR_80
cur_mode:   db 1
bg_cfg:     db #C4
dirty_ptr:  dw dlist_c0
dend_c0:    dw dlist_c0
dend_80:    dw dlist_80
dlist_c0:   defs 32*4,0
dlist_80:   defs 32*4,0
lag_count:  db 0
rr_cnt:     db 0
dm_w:       db 0
dm_h:       db 0
dm_src:     dw 0
op_x:       db 0
op_y:       db 0
op_w:       db 0
op_h:       db 0
op_src:     dw 0
op_vis:     db 0
op_s2:      dw 0
txt_fg:     db 1
txt_bg:     db 0
tx_scr:     dw 0
tx_rows:    db 0
tl_stride:  dw 40

; overlay (ov_x..ov_h must stay in this order)
ov_on:      db 0
ov_x:       db 0
ov_y:       db 0
ov_w:       db 0
ov_h:       db 0
ov_wcols:   db 0
ov_col:     db 0
ov_pc_c0:   dw 0
ov_pc_80:   dw 0
ov_closing: db 0
os_slot:    dw 0
os_budget:  db 0

; hud
hud_pend_c0: db 0
hud_pend_80: db 0
hs_flags:   db 0
hs_pos:     db 0
tick_pos_c0: db 40
tick_pos_80: db 40
tick_buf:   defs 40,32
tick_tmp:   db TX_FG,1,TX_BG,0,32,32,0
tick_col:   db 1
num_buf:    defs 10,0
str_buf:    defs 12,0
as_op:      defs 3,0

; game
inp:        db 0
inp_new:    db 0
seed:       dw #ACE1
cur_set:    dw spr_set_ep1
diff_ptr:   dw diff_tab
difficulty: db 1
lives:      db 3
miss_limit: db 3
misses:     db 0
score:      defs 3,0
hiscore:    db #00,#50,#00
episode:    db 0
start_ep:   db 0
wave:       db 0
loop_n:     db 0
quit_flag:  db 0
level:      db 0
fall_spd:   dw #0100
spawn_int:  db 30
spawn_timer: db 30
item_cap:  db 4
quota_left: db 10
obst_int:   db 200
obst_timer: db 200
cool_max:   db 4
state:      db 0
state_timer: db 0
streak:     db 0
mult:       db 1
ep_raster:  dw rast_ep1
ep_card:    dw 0
ep_pen0:    db 0
ep_shelf1:  db 0
shelf_flash: db 0
life_flash: db 0
bolt_cur:   dw 0

; objects (cleared together by reset_objects)
items:      defs MAX_ITEMS*IT_SIZE,0
bolts:      defs MAX_BOLTS*2,0
poofs:      defs MAX_POOFS*4,0
bros:       defs MAX_BROS*BR_SIZE,0
player_x:   db 0
player_hold: db 0
player_dir: db 0
player_zap: db 0
player_slow: db 0
player_cool: db 0
robot_x:    db 0
robot_dx:   db 0
robot_print: db 0
popup_on:   db 0
popup_hp:   db 0
popup_life: db 0
ban_on:     db 0
ban_x:      db 0
ban_y:      db 0
ban_dx:     db 0
ban_hp:     db 0
objects_end:

; obstacles
pp_x:       db 0
pp_y:       db 0
pp_txt:     dw 0
popup_cmds: defs 60,0
ban_buf:    defs BAN_W*BAN_H,0

; menu
menu_page:  db 0
page_timer: db 0
scr_ptr:    dw 0
scr_col:    db 0
rb_phase:   db 0
opt_buf:    defs 24,0
