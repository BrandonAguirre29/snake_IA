# ─── menu.py ─────────────────────────────────────────────────
# Todas las pantallas de interfaz: Menú, Game Over, Victoria

import pygame
import math

BLACK        = (0,   0,   0  )
GREEN_BRIGHT = (0,   255, 80 )
GREEN_DARK   = (0,   140, 40 )
GREEN_NEON   = (0,   255, 120)
WHITE        = (255, 255, 255)
GRAY         = (130, 130, 130)
RED          = (220, 50,  50 )
RED_DARK     = (120, 20,  20 )
YELLOW       = (255, 215, 0  )
GRID_COL     = (15,  15,  15 )
CYAN         = (0,   200, 220)

LEVEL_COLORS = {
    1: {
        "bg":      (0,  100, 30),  "bg_hov":  (0,  220, 80),
        "fg":      GREEN_BRIGHT,   "fg_hov":  BLACK,
        "brd":     GREEN_DARK,     "brd_hov": WHITE,
    },
    2: {
        "bg":      (120, 100, 0),  "bg_hov":  (255, 215, 0),
        "fg":      YELLOW,         "fg_hov":  BLACK,
        "brd":     (160, 130, 0),  "brd_hov": WHITE,
    },
    3: {
        "bg":      (100, 15, 15),  "bg_hov":  (220, 50, 50),
        "fg":      (255, 120, 120),"fg_hov":  WHITE,
        "brd":     (140, 20, 20),  "brd_hov": WHITE,
    },
}

pygame.font.init()
font_huge  = pygame.font.SysFont("consolas", 72, bold=True)
font_big   = pygame.font.SysFont("consolas", 48, bold=True)
font_med   = pygame.font.SysFont("consolas", 24, bold=True)
font_small = pygame.font.SysFont("consolas", 18)
font_tiny  = pygame.font.SysFont("consolas", 13)


def get_dims(win):
    W, H = win.get_size()
    return W, H, W // 2, H // 2

def draw_bg(surface):
    W, H, _, _ = get_dims(surface)
    surface.fill((5, 8, 5))
    cell = 30
    for x in range(0, W, cell):
        pygame.draw.line(surface, GRID_COL, (x, 0), (x, H))
    for y in range(0, H, cell):
        pygame.draw.line(surface, GRID_COL, (0, y), (W, y))

def draw_centered_text(surface, text, font, color, cy, shadow=True):
    _, _, CX, _ = get_dims(surface)
    if shadow:
        sh = font.render(text, True, (0, 30, 0))
        surface.blit(sh, (CX - sh.get_width()//2 + 2, cy + 2))
    t = font.render(text, True, color)
    surface.blit(t, (CX - t.get_width()//2, cy))
    return t.get_height()

def draw_button(surface, text, cy, hovered, tick):
    _, _, CX, _ = get_dims(surface)
    bw, bh = 280, 50
    bx, by = CX - bw//2, cy - bh//2
    if hovered:
        bg, fg, brd = GREEN_BRIGHT, BLACK, WHITE
    else:
        pulse = abs(math.sin(tick * 0.06))
        bg  = (0, int(60 + pulse*40), int(15 + pulse*15))
        fg  = GREEN_BRIGHT
        brd = GREEN_DARK
    pygame.draw.rect(surface, bg,  (bx, by, bw, bh), border_radius=10)
    pygame.draw.rect(surface, brd, (bx, by, bw, bh), 2, border_radius=10)
    t = font_med.render(text, True, fg)
    surface.blit(t, (CX - t.get_width()//2, cy - t.get_height()//2))
    return pygame.Rect(bx, by, bw, bh)

def draw_level_button(surface, text, cx, cy, hovered, level_num):
    bw, bh = 95, 65
    bx, by = cx - bw//2, cy - bh//2
    cols = LEVEL_COLORS[level_num]
    bg  = cols["bg_hov"]  if hovered else cols["bg"]
    fg  = cols["fg_hov"]  if hovered else cols["fg"]
    brd = cols["brd_hov"] if hovered else cols["brd"]
    pygame.draw.rect(surface, bg,  (bx, by, bw, bh), border_radius=8)
    pygame.draw.rect(surface, brd, (bx, by, bw, bh), 2, border_radius=8)
    num = font_med.render(str(level_num), True, fg)
    surface.blit(num, (cx - num.get_width()//2, cy - num.get_height()//2 - 7))
    lbl = font_tiny.render(text, True, fg)
    surface.blit(lbl, (cx - lbl.get_width()//2, cy + 14))
    return pygame.Rect(bx, by, bw, bh)

def is_hovered(mx, my, cx, cy, bw=280, bh=50):
    return abs(mx - cx) < bw//2 and abs(my - cy) < bh//2

def is_hovered_lvl(mx, my, cx, cy, bw=95, bh=65):
    return abs(mx - cx) < bw//2 and abs(my - cy) < bh//2

def draw_snake_art(surface, cx, cy, cell=18, tick=0):
    segments = [
        (0,0),(1,0),(2,0),(3,0),(4,0),(5,0),
        (5,1),(5,2),
        (4,2),(3,2),(2,2),(1,2),(0,2),
        (0,3),(0,4),
        (1,4),(2,4),(3,4),(4,4),(5,4),
    ]
    min_x = min(s[0] for s in segments)
    max_x = max(s[0] for s in segments)
    min_y = min(s[1] for s in segments)
    total_w = (max_x - min_x + 1) * cell
    ox = cx - total_w // 2
    oy = cy

    for i, (gx, gy) in enumerate(segments):
        px, py = ox + gx*cell, oy + gy*cell
        if i == 0:
            pygame.draw.rect(surface, GREEN_NEON,  (px+1, py+1, cell-2, cell-2), border_radius=4)
            pygame.draw.rect(surface, WHITE,        (px+1, py+1, cell-2, cell-2), 2, border_radius=4)
            pygame.draw.circle(surface, BLACK, (px+5,      py+6), 2)
            pygame.draw.circle(surface, BLACK, (px+cell-6, py+6), 2)
        else:
            color = GREEN_BRIGHT if i % 2 == 0 else GREEN_DARK
            pygame.draw.rect(surface, color, (px+2, py+2, cell-4, cell-4), border_radius=3)

    pulse = int(math.sin(tick * 0.08))
    ax  = ox + (max_x + 2) * cell
    acx = ax + cell//2
    acy = oy + cell//2
    r   = cell//2 - 1 + pulse
    pygame.draw.circle(surface, RED_DARK,     (acx+2, acy+2), r)
    pygame.draw.circle(surface, RED,           (acx,   acy  ), r)
    pygame.draw.circle(surface, (255,120,120), (acx-2, acy-2), max(1, r//3))
    pygame.draw.line  (surface, (80,50,20),    (acx, acy-r), (acx+2, acy-r-3), 2)
    pygame.draw.ellipse(surface, (0,180,0),    (acx+1, acy-r-3, 5, 3))


# ─────────────────────────────────────────────────────────────
# MENU PRINCIPAL
# ─────────────────────────────────────────────────────────────

def show_menu(win):
    clock      = pygame.time.Clock()
    tick       = 0
    btn_rect   = pygame.Rect(0, 0, 1, 1)
    salir_rect = pygame.Rect(0, 0, 1, 1)
    lvl_rects  = {1: pygame.Rect(0,0,1,1),
                  2: pygame.Rect(0,0,1,1),
                  3: pygame.Rect(0,0,1,1)}

    while True:
        clock.tick(30)
        tick += 1
        W, H, CX, CY = get_dims(win)
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); return False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE): return 1
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_rect.collidepoint(mx, my):    return 1
                if salir_rect.collidepoint(mx, my):
                    pygame.quit(); return False
                for num, rect in lvl_rects.items():
                    if rect.collidepoint(mx, my):    return num

        draw_bg(win)

        # ── Layout proporcional centrado en H ──
        # Altura total del bloque de contenido: ~480px
        # Lo centramos verticalmente dejando margen arriba y abajo
        block_h  = 480
        top      = (H - block_h) // 2          # margen superior dinámico

        snake_y    = top
        title_y    = snake_y  + 105
        sub_y      = title_y  + 78
        sep1_y     = sub_y    + 22
        btn_y      = sep1_y   + 42
        sep2_y     = btn_y    + 38
        lv_title_y = sep2_y   + 12
        lv_y       = lv_title_y + 46
        salir_y    = lv_y     + 56
        cred1_y    = H - 40
        cred2_y    = H - 22

        # Serpiente
        draw_snake_art(win, CX, snake_y, cell=18, tick=tick)

        # Titulo
        pulse     = abs(math.sin(tick * 0.05))
        title_col = (int(pulse*10), int(210+pulse*45), int(80+pulse*40))
        draw_centered_text(win, "SNAKE", font_huge, title_col, title_y)

        # Subtitulo
        draw_centered_text(win, "Adaptativo  —  IA", font_small, GRAY, sub_y, shadow=False)

        # Separador 1
        pygame.draw.line(win, GREEN_DARK, (CX-130, sep1_y), (CX+130, sep1_y), 1)

        # Boton INICIAR
        btn_rect = draw_button(win, "INICIAR", btn_y, is_hovered(mx, my, CX, btn_y), tick)

        # Separador 2
        pygame.draw.line(win, GREEN_DARK, (CX-130, sep2_y), (CX+130, sep2_y), 1)

        # Titulo seccion niveles
        lv_title = font_tiny.render("— Elegir nivel —", True, GRAY)
        win.blit(lv_title, (CX - lv_title.get_width()//2, lv_title_y))

        # Botones de nivel en fila
        gap    = 110
        lv_cx  = {1: CX - gap, 2: CX, 3: CX + gap}
        labels = {1: "Facil", 2: "Medio", 3: "Dificil"}
        for num in (1, 2, 3):
            hov = is_hovered_lvl(mx, my, lv_cx[num], lv_y)
            lvl_rects[num] = draw_level_button(win, labels[num], lv_cx[num], lv_y, hov, num)

        # Boton Salir
        salir_bw, salir_bh = 140, 32
        salir_bx  = CX - salir_bw//2
        salir_by  = salir_y - salir_bh//2
        salir_hov = abs(mx-CX) < salir_bw//2 and abs(my-salir_y) < salir_bh//2
        salir_bg  = (180, 30, 30) if salir_hov else (60, 10, 10)
        salir_fg  = WHITE         if salir_hov else (180, 80, 80)
        pygame.draw.rect(win, salir_bg,      (salir_bx, salir_by, salir_bw, salir_bh), border_radius=7)
        pygame.draw.rect(win, (120, 20, 20), (salir_bx, salir_by, salir_bw, salir_bh), 1, border_radius=7)
        st = font_small.render("Salir", True, salir_fg)
        win.blit(st, (CX - st.get_width()//2, salir_y - st.get_height()//2))
        salir_rect = pygame.Rect(salir_bx, salir_by, salir_bw, salir_bh)

        # Creditos fijos abajo
        ctrl = font_tiny.render("Flechas para mover  |  ESC para salir", True, (55, 55, 55))
        win.blit(ctrl, (CX - ctrl.get_width()//2, cred1_y))
        cred = font_tiny.render(
            "Universidad Tecnologica de Nayarit  —  Aprendizaje Maquina  2025", True, (38, 38, 38))
        win.blit(cred, (CX - cred.get_width()//2, cred2_y))

        pygame.display.flip()


# ─────────────────────────────────────────────────────────────
# GAME OVER
# ─────────────────────────────────────────────────────────────

def show_game_over(win, score, level, data_count):
    clock         = pygame.time.Clock()
    tick          = 0
    btn_reiniciar = pygame.Rect(0, 0, 1, 1)
    btn_menu      = pygame.Rect(0, 0, 1, 1)

    while True:
        clock.tick(30)
        tick += 1
        W, H, CX, CY = get_dims(win)
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:                    return True
                if event.key in (pygame.K_q, pygame.K_ESCAPE): return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_reiniciar.collidepoint(mx, my): return True
                if btn_menu.collidepoint(mx, my):      return False

        draw_bg(win)
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((60, 0, 0, 185))
        win.blit(overlay, (0, 0))

        pulse     = abs(math.sin(tick * 0.08))
        title_col = (int(200+pulse*55), int(30+pulse*20), 30)
        title_y   = H // 5
        draw_centered_text(win, "GAME OVER", font_big, title_col, title_y)

        sep1_y = title_y + 70
        pygame.draw.line(win, RED, (CX-200, sep1_y), (CX+200, sep1_y), 1)

        s1_y = sep1_y + 22
        draw_centered_text(win, f"Puntuacion:   {score}", font_med, WHITE, s1_y,      shadow=False)
        draw_centered_text(win, f"Nivel:        {level}", font_med, GRAY,  s1_y + 40, shadow=False)

        sep2_y = s1_y + 85
        pygame.draw.line(win, RED, (CX-200, sep2_y), (CX+200, sep2_y), 1)

        br_y = sep2_y + 55
        bm_y = sep2_y + 120
        btn_reiniciar = draw_button(win, "REINICIAR", br_y, is_hovered(mx, my, CX, br_y), tick)
        btn_menu      = draw_button(win, "SALIR",     bm_y, is_hovered(mx, my, CX, bm_y), tick)

        hint = font_tiny.render("R = Reiniciar   |   ESC = Salir", True, (55,55,55))
        win.blit(hint, (CX - hint.get_width()//2, H - 28))
        pygame.display.flip()


# ─────────────────────────────────────────────────────────────
# VICTORIA
# ─────────────────────────────────────────────────────────────

def show_victory(win, score, data_count):
    clock         = pygame.time.Clock()
    tick          = 0
    btn_reiniciar = pygame.Rect(0, 0, 1, 1)
    btn_salir     = pygame.Rect(0, 0, 1, 1)

    while True:
        clock.tick(30)
        tick += 1
        W, H, CX, CY = get_dims(win)
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:                    return True
                if event.key in (pygame.K_q, pygame.K_ESCAPE): pygame.quit(); return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_reiniciar.collidepoint(mx, my): return True
                if btn_salir.collidepoint(mx, my):     pygame.quit(); return False

        draw_bg(win)
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 60, 20, 160))
        win.blit(overlay, (0, 0))

        snake_y = H // 6
        draw_snake_art(win, CX, snake_y, cell=16, tick=tick)

        pulse     = abs(math.sin(tick * 0.07))
        title_col = (int(80 + pulse*175), int(230 + pulse*25), int(80 + pulse*40))
        title_y   = snake_y + 80
        draw_centered_text(win, "YOU WIN!", font_huge, title_col, title_y)

        sep_y = title_y + 95
        pygame.draw.line(win, GREEN_NEON, (CX-180, sep_y), (CX+180, sep_y), 1)

        sub_col = (int(200 + pulse*55), int(220 + pulse*35), int(100 + pulse*50))
        draw_centered_text(win, "Felicidades!", font_big, sub_col, sep_y + 22, shadow=False)

        sep2_y = sep_y + 80
        pygame.draw.line(win, GREEN_DARK, (CX-180, sep2_y), (CX+180, sep2_y), 1)

        br_y = sep2_y + 52
        bs_y = sep2_y + 115
        btn_reiniciar = draw_button(win, "REINICIAR", br_y, is_hovered(mx, my, CX, br_y), tick)
        btn_salir     = draw_button(win, "SALIR",     bs_y, is_hovered(mx, my, CX, bs_y), tick)

        hint = font_tiny.render("R = Reiniciar   |   ESC = Salir", True, (55, 55, 55))
        win.blit(hint, (CX - hint.get_width()//2, H - 28))
        pygame.display.flip()