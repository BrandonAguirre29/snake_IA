# ─── config.py ───────────────────────────────────────────────
# Constantes globales del juego. Todos los módulos importan de aquí.

WIDTH  = 500
HEIGHT = 500
ROWS   = 20
FPS    = 10

# ── Colores ──
BLACK        = (0,   0,   0  )
GRID_COLOR   = (25,  25,  25 )
GREEN_BRIGHT = (0,   255, 80 )
GREEN_DARK   = (0,   180, 50 )
HEAD_COLOR   = (0,   255, 120)
RED_APPLE    = (255, 40,  40 )
POISON_COL   = (160, 0,   200)
POISON_GLOW  = (200, 80,  255)
WHITE        = (255, 255, 255)
GRAY         = (100, 100, 100)
YELLOW       = (255, 220, 0  )
OBSTACLE_COL = (180, 60,  60 )
OBSTACLE_BRD = (255, 80,  80 )
HEART_RED    = (255, 60,  60 )
LIFE_COL     = (255, 215, 0  )
LIFE_GLOW    = (255, 255, 150)
WALL_COL     = (60,  80,  120)
WALL_BRD     = (100, 140, 200)
LEVEL_FLASH  = (0,   180, 255)

# ── Música por nivel ──
MUSIC_FILES = {
    1:    "music/Level1.mp3",
    3:    "music/Level3.mp3",   # nivel 2 eliminado, usamos Level3 para el nivel 3
    "4a": "music/Level4.mp3",
    "4b": "music/FinalBoss.mp3",
}
MUSIC_GAMEOVER = "music/GameOver.mp3"
MUSIC_WIN      = "music/Win.mp3"
MUSIC_VOLUME   = 0.5

# ── Pausa al perder una vida (en milisegundos) ──
# El jugador ve el flash rojo y tiene tiempo de orientarse antes de seguir.
HIT_PAUSE_MS = 1200
