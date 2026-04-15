import math
import pygame
from config import *

pygame.font.init()
font_score  = pygame.font.SysFont("consolas", 20, bold=True)
font_big    = pygame.font.SysFont("consolas", 44, bold=True)
font_medium = pygame.font.SysFont("consolas", 22)
font_small  = pygame.font.SysFont("consolas", 15)

DIS = WIDTH // ROWS

RIVAL_COLOR = (220, 60, 60)

# Colores del arcoiris para la manzana vida
RAINBOW_COLS = [
    (255, 77,  77 ),
    (255, 170,  0 ),
    (68,  221, 102),
    (68,  136, 255),
    (170,  68, 255),
    (255,  77, 170),
]

# Colores del arcoiris para la SERPIENTE
RAINBOW_SNAKE = [
    (  0, 230, 118),  # 0  verde brillante (cabeza)
    (118, 255,   3),  # 1  verde-amarillo
    (255, 234,   0),  # 2  amarillo
    (255, 145,   0),  # 3  naranja
    (255,  61,   0),  # 4  rojo-naranja
    (245,   0,  87),  # 5  rosa/magenta
    (213,   0, 249),  # 6  violeta
    (101,  31, 255),  # 7  azul-violeta
    ( 41, 121, 255),  # 8  azul
    (  0, 229, 255),  # 9  cian
]


def draw_snake(surface, body):
    """Dibuja la serpiente con colores de arcoiris por segmento."""
    total_colors = len(RAINBOW_SNAKE)

    for i, segment in enumerate(body):
        px, py = segment.pos[0] * DIS, segment.pos[1] * DIS

        color      = RAINBOW_SNAKE[i % total_colors]
        r, g, b    = color
        border_col = (min(255, r + 60), min(255, g + 60), min(255, b + 60))

        if i == 0:
            # Cabeza con ojos
            pygame.draw.rect(surface, color,
                             (px + 1, py + 1, DIS - 2, DIS - 2),
                             border_radius=7)
            pygame.draw.rect(surface, border_col,
                             (px + 1, py + 1, DIS - 2, DIS - 2),
                             2, border_radius=7)
            eye_r = max(2, DIS // 8)
            pygame.draw.circle(surface, (255, 255, 255),
                               (px + DIS // 3,     py + DIS // 3), eye_r)
            pygame.draw.circle(surface, (255, 255, 255),
                               (px + 2 * DIS // 3, py + DIS // 3), eye_r)
            pygame.draw.circle(surface, (10, 10, 10),
                               (px + DIS // 3,     py + DIS // 3), max(1, eye_r - 1))
            pygame.draw.circle(surface, (10, 10, 10),
                               (px + 2 * DIS // 3, py + DIS // 3), max(1, eye_r - 1))
        else:
            # Cuerpo con margen alterno para efecto de escamas
            margin = 2 + (i % 2)
            pygame.draw.rect(surface, color,
                             (px + margin, py + margin,
                              DIS - margin * 2, DIS - margin * 2),
                             border_radius=5)
            pygame.draw.rect(surface, border_col,
                             (px + margin, py + margin,
                              DIS - margin * 2, DIS - margin * 2),
                             1, border_radius=5)


def draw_grid(surface):
    for l in range(ROWS):
        x = (l + 1) * DIS
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, HEIGHT))
        pygame.draw.line(surface, GRID_COLOR, (0, x), (WIDTH, x))


def draw_walls(surface, walls):
    for (wx, wy) in walls:
        px, py = wx * DIS, wy * DIS
        pygame.draw.rect(surface, (30, 37, 53),  (px+1, py+1, DIS-2, DIS-2), border_radius=3)
        pygame.draw.rect(surface, (0, 200, 200), (px+1, py+1, DIS-2, DIS-2), 2, border_radius=3)
        pygame.draw.rect(surface, (20, 29, 46),  (px+4, py+4, DIS-8, DIS-8), border_radius=2)


def draw_obstacles(surface, obstacles):
    for (ox, oy) in obstacles:
        px, py = ox * DIS, oy * DIS
        pygame.draw.rect(surface, (74, 10, 10),   (px+1, py+1, DIS-2, DIS-2), border_radius=4)
        pygame.draw.rect(surface, (204, 34, 102), (px+1, py+1, DIS-2, DIS-2), 2, border_radius=4)
        pygame.draw.line(surface, (204, 34, 102), (px+5, py+5), (px+DIS-6, py+DIS-6), 2)
        pygame.draw.line(surface, (204, 34, 102), (px+DIS-6, py+5), (px+5, py+DIS-6), 2)


def draw_apple(surface, pos):
    px, py = pos[0] * DIS, pos[1] * DIS
    cx, cy = px + DIS // 2, py + DIS // 2
    r      = DIS // 2 - 2
    pygame.draw.circle(surface, (120, 0, 0),    (cx+2, cy+2), r)
    pygame.draw.circle(surface, RED_APPLE,       (cx,   cy  ), r)
    pygame.draw.circle(surface, (255, 130, 130), (cx-3, cy-3), r//3)
    pygame.draw.line  (surface, (80, 50, 20),    (cx, cy-r), (cx+3, cy-r-5), 2)
    pygame.draw.ellipse(surface, (0, 180, 0),    (cx+2, cy-r-5, 7, 4))


def draw_poison_apple(surface, pos, tick):
    px, py = pos[0] * DIS, pos[1] * DIS
    cx, cy = px + DIS // 2, py + DIS // 2
    r      = DIS // 2 - 2
    pulse  = int(math.sin(tick * 0.15) * 2)

    ring_phase = tick % 60
    for offset in [0, 20, 40]:
        phase      = (ring_phase + offset) % 60
        ring_r     = r + 4 + int(phase * 0.35)
        ring_alpha = max(0, 200 - int(phase * 3.3))
        ring_surf  = pygame.Surface((ring_r*2+2, ring_r*2+2), pygame.SRCALPHA)
        pygame.draw.circle(ring_surf, (220, 0, 0, ring_alpha),
                           (ring_r+1, ring_r+1), ring_r, 2)
        surface.blit(ring_surf, (cx - ring_r - 1, cy - ring_r - 1))

    pygame.draw.circle(surface, (68, 0, 0),      (cx+2, cy+2), r+pulse)
    pygame.draw.circle(surface, (204, 0, 0),     (cx,   cy  ), r+pulse)
    pygame.draw.circle(surface, (255, 102, 102), (cx-3, cy-3), max(1, (r+pulse)//3))
    pygame.draw.line  (surface, (80, 50, 20),    (cx, cy-r-pulse), (cx+3, cy-r-pulse-5), 2)
    pygame.draw.ellipse(surface, (136, 0, 0),    (cx+2, cy-r-pulse-5, 7, 4))
    pygame.draw.rect(surface, WHITE, (cx-2, cy-5, 4, 9), border_radius=2)
    pygame.draw.circle(surface, WHITE, (cx, cy+7), 2)


def draw_life_apple(surface, pos, tick):
    px, py = pos[0] * DIS, pos[1] * DIS
    cx, cy = px + DIS // 2, py + DIS // 2
    r      = DIS // 2 - 2
    pulse  = int(math.sin(tick * 0.2) * 2)

    ring_phase = tick % 60
    for offset in [0, 20, 40]:
        phase      = (ring_phase + offset) % 60
        ring_r     = r + 4 + int(phase * 0.35)
        ring_alpha = max(0, 200 - int(phase * 3.3))
        ring_surf  = pygame.Surface((ring_r*2+2, ring_r*2+2), pygame.SRCALPHA)
        pygame.draw.circle(ring_surf, (0, 220, 80, ring_alpha),
                           (ring_r+1, ring_r+1), ring_r, 2)
        surface.blit(ring_surf, (cx - ring_r - 1, cy - ring_r - 1))

    col_idx  = (tick // 8) % len(RAINBOW_COLS)
    col_next = (col_idx + 1) % len(RAINBOW_COLS)
    t_frac   = (tick % 8) / 8.0
    r0, g0, b0 = RAINBOW_COLS[col_idx]
    r1, g1, b1 = RAINBOW_COLS[col_next]
    body_col = (
        int(r0 + (r1 - r0) * t_frac),
        int(g0 + (g1 - g0) * t_frac),
        int(b0 + (b1 - b0) * t_frac),
    )

    pygame.draw.circle(surface, (0, 34, 0),        (cx+2, cy+2), r+pulse)
    pygame.draw.circle(surface, body_col,           (cx,   cy  ), r+pulse)
    pygame.draw.circle(surface, (255, 255, 255),   (cx-3, cy-3), max(1, (r+pulse)//3))
    pygame.draw.line  (surface, (80, 50, 20),      (cx, cy-r-pulse), (cx+3, cy-r-pulse-5), 2)
    pygame.draw.ellipse(surface, (0, 200, 0),      (cx+2, cy-r-pulse-5, 7, 4))
    pygame.draw.line(surface, WHITE, (cx-5, cy), (cx+5, cy), 2)
    pygame.draw.line(surface, WHITE, (cx, cy-5), (cx, cy+5), 2)


def draw_hearts(surface, lives, max_lives=3):
    for i in range(max_lives):
        x = WIDTH - 28 - i * 28
        y = 28
        pts = [(x-11, y-1), (x-5, y-9), (x, y-5), (x+5, y-9), (x+11, y-1), (x, y+11)]
        if i < lives:
            pygame.draw.polygon(surface, HEART_RED, pts)
        else:
            pygame.draw.polygon(surface, GRAY, pts, 2)


def draw_hud(surface, score, lives, level, data_count, obstacles_placed,
             fase_4b=False, rival=None, snack_timer=None):
    sc  = font_score.render(f"Score: {score}/30", True, GREEN_BRIGHT)
    dat = font_small.render(f"Datos: {data_count}", True, GRAY)
    obs = font_small.render(f"Obs.IA: {obstacles_placed}", True, OBSTACLE_BRD)

    if level == 4:
        if fase_4b:
            lv_text = "NIVEL 4 - TE PERSIGUE!"
            lv_col  = (255, 80, 80)
        else:
            lv_text = "NIVEL 4 - Rival activo"
            lv_col  = LEVEL_FLASH
    else:
        lv_text = f"Nivel {level}"
        lv_col  = LEVEL_FLASH

    lv  = font_score.render(lv_text, True, lv_col)
    leg = font_small.render("! = veneno (-vida)    + = vida extra", True, (255, 80, 80))

    surface.blit(sc,  (8, 6))
    surface.blit(lv,  (WIDTH//2 - lv.get_width()//2, 6))
    surface.blit(dat, (8, 30))
    surface.blit(obs, (8, 46))
    surface.blit(leg, (WIDTH//2 - leg.get_width()//2, HEIGHT - 20))
    draw_hearts(surface, lives)

    if rival is not None:
        rv_col = (255, 80, 80) if rival.lives <= 1 else (220, 140, 60)
        for i in range(3):
            rx  = WIDTH - 28 - i * 18
            ry  = 50
            col = (200, 40, 40) if i < rival.lives else (60, 20, 20)
            pygame.draw.rect(surface, col, (rx-6, ry-6, 12, 12), border_radius=3)
        spd = font_small.render(rival.speed_label, True, rv_col)
        surface.blit(spd, (WIDTH - spd.get_width() - 8, 62))

    if snack_timer is not None:
        bar_w  = 80
        filled = int(bar_w * snack_timer / 12)
        filled = max(0, min(bar_w, filled))
        bar_col = GREEN_BRIGHT if snack_timer > 48 else YELLOW if snack_timer > 24 else (255, 60, 60)
        pygame.draw.rect(surface, GRAY,    (WIDTH - bar_w - 8, 8, bar_w, 7), border_radius=3)
        pygame.draw.rect(surface, bar_col, (WIDTH - bar_w - 8, 8, filled, 7), border_radius=3)
        tt = font_small.render("manzana", True, GRAY)
        surface.blit(tt, (WIDTH - tt.get_width() - 8, 17))


def draw_level_up(surface, level):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    surface.blit(overlay, (0, 0))

    msgs = {
        2: "Mapa reducido! Manzanas se mueven!",
        3: "APARECE EL RIVAL!",
    }
    t   = font_big.render(f"NIVEL {level}!", True, LEVEL_FLASH)
    sub = font_medium.render(msgs.get(level, "Sigue adelante!"), True, WHITE)
    surface.blit(t,   (WIDTH//2 - t.get_width()//2,   HEIGHT//2 - 35))
    surface.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 20))
    pygame.display.flip()
    pygame.time.delay(1400)


def draw_fase_4b_warning(surface):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((80, 0, 0, 160))
    surface.blit(overlay, (0, 0))
    t   = font_big.render("TE VIENE A BUSCAR!", True, (255, 80, 80))
    sub = font_medium.render("El rival ahora va por ti...", True, WHITE)
    surface.blit(t,   (WIDTH//2 - t.get_width()//2,   HEIGHT//2 - 35))
    surface.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 20))
    pygame.display.flip()
    pygame.time.delay(1600)


def draw_you_win(surface, score, data_count, tick):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 26, 6, 210))
    surface.blit(overlay, (0, 0))

    pulse_alpha = int(180 + math.sin(tick * 0.08) * 75)
    pulse_alpha = max(0, min(255, pulse_alpha))

    ring_phase = tick % 60
    for offset in [0, 20, 40]:
        phase      = (ring_phase + offset) % 60
        ring_w     = 260 + int(phase * 2.5)
        ring_h     = 32  + int(phase * 0.4)
        ring_alpha = max(0, 180 - int(phase * 3))
        ring_surf  = pygame.Surface((ring_w*2, ring_h*2), pygame.SRCALPHA)
        pygame.draw.ellipse(ring_surf, (255, 215, 0, ring_alpha),
                            (0, 0, ring_w*2, ring_h*2), 2)
        surface.blit(ring_surf, (WIDTH//2 - ring_w, HEIGHT//2 - 110 - ring_h + 20))

    t_surf = font_big.render("GANASTE!", True, (255, 215, 0))
    t_surf.set_alpha(pulse_alpha)
    surface.blit(t_surf, (WIDTH//2 - t_surf.get_width()//2, HEIGHT//2 - 110))

    sc = font_medium.render(f"Puntuacion final: {score}",        True, WHITE)
    d  = font_medium.render(f"Datos recolectados: {data_count}", True, (0, 230, 118))
    r  = font_medium.render("R = Jugar de nuevo    Q = Salir",   True, (85, 85, 85))

    surface.blit(sc, (WIDTH//2 - sc.get_width()//2, HEIGHT//2 - 45))
    surface.blit(d,  (WIDTH//2 - d.get_width()//2,  HEIGHT//2 - 5 ))
    surface.blit(r,  (WIDTH//2 - r.get_width()//2,  HEIGHT//2 + 55))


def draw_game_over(surface, score, level, data_count):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((26, 0, 0, 210))
    surface.blit(overlay, (0, 0))

    t  = font_big.render("GAME OVER",                                True, (255, 34,  34 ))
    sc = font_medium.render(f"Puntuacion: {score}  |  Nivel: {level}", True, (255, 170, 170))
    d  = font_medium.render(f"Datos totales: {data_count}",             True, (255, 136,  85))

    if data_count < 200:
        msg, col = "Sigue jugando para mejorar la IA!", (170, 85, 85)
    elif data_count < 600:
        msg, col = "La IA ya aprende tu estilo!",        (255, 204, 68)
    else:
        msg, col = "La IA te conoce muy bien!",          (255, 204, 68)

    m = font_small.render(msg,                            True, col)
    r = font_medium.render("R = Reiniciar    Q = Salir", True, (119, 51, 51))

    surface.blit(t,  (WIDTH//2 - t.get_width()//2,  HEIGHT//2 - 110))
    surface.blit(sc, (WIDTH//2 - sc.get_width()//2, HEIGHT//2 - 45))
    surface.blit(d,  (WIDTH//2 - d.get_width()//2,  HEIGHT//2 - 5 ))
    surface.blit(m,  (WIDTH//2 - m.get_width()//2,  HEIGHT//2 + 35))
    surface.blit(r,  (WIDTH//2 - r.get_width()//2,  HEIGHT//2 + 68))


def draw_flash(surface):
    flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    flash.fill((180, 0, 80, 85))
    surface.blit(flash, (0, 0))


def redraw(win, snake, snack, poison_apple, life_apple,
           walls, obstacles, score, lives, level,
           data_count, obstacles_placed, tick,
           rival=None, fase_4b=False,
           flash=False, game_over=False, you_win=False,
           snack_timer=None):
    win.fill(BLACK)
    draw_grid(win)
    draw_walls(win, walls)
    draw_obstacles(win, obstacles)
    if rival:
        rival.draw(win)
    draw_snake(win, snake.body)   # <-- serpiente arcoiris
    draw_apple(win, snack.pos)
    if poison_apple:
        draw_poison_apple(win, poison_apple, tick)
    if life_apple:
        draw_life_apple(win, life_apple, tick)
    draw_hud(win, score, lives, level, data_count, obstacles_placed,
             fase_4b, rival=rival, snack_timer=snack_timer)
    if flash:
        draw_flash(win)
    if you_win:
        draw_you_win(win, score, data_count, tick)
    elif game_over:
        draw_game_over(win, score, level, data_count)
    pygame.display.update()