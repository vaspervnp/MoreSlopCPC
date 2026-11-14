; ============================================================================
; game data that must stay in LOW
; ============================================================================

; difficulty: lives, misses per life, fall speed (8.8), fall increase per
; level, frames between prints, max items, quota, frames between obstacles,
; zap cooldown
diff_tab:
    db 5,5 : dw #00D0 : db 4,34,3,10,230,3      ; TOUCH GRASS
    db 3,3 : dw #0118 : db 6,27,4,14,180,4      ; TERMINALLY ONLINE
    db 2,3 : dw #0160 : db 8,21,5,18,140,5      ; SINGULARITY

; points per slop kind (BCD)
kind_points: db #10,#25,#15

; raster table that changes nothing
rast_none: dw 0,0,0,0,0,0
