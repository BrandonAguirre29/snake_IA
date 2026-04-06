import math
import random
import pygame
import csv
import os
from collections import Counter

# ─── CONFIGURACIÓN ───────────────────────────────────────────
width  = 500
height = 500
rows   = 20

# Colores
BLACK        = (0,   0,   0  )
GRID_COLOR   = (25,  25,  25 )
GREEN_BRIGHT = (0,   255, 80 )
GREEN_DARK   = (0,   180, 50 )
HEAD_COLOR   = (0,   255, 120)
RED_APPLE    = (255, 40,  40 )
WHITE        = (255, 255, 255)
GRAY         = (100, 100, 100)
YELLOW       = (255, 220, 0  )
OBSTACLE_COL = (180, 60,  60 )   # color de obstáculos IA
OBSTACLE_BRD = (255, 80,  80 )   # borde obstáculos

pygame.init()
font_score  = pygame.font.SysFont("consolas", 20, bold=True)
font_big    = pygame.font.SysFont("consolas", 44, bold=True)
font_medium = pygame.font.SysFont("consolas", 22)
font_small  = pygame.font.SysFont("consolas", 15)

# ─── CSV ─────────────────────────────────────────────────────
CSV_FILE = "snake_data.csv"

def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            csv.writer(f).writerow([
                "x", "y",           # posición de la cabeza
                "dir",              # 0=arr 1=abj 2=izq 3=der
                "length",           # longitud actual
                "zone",             # 0=arriba-izq 1=arriba-der 2=abajo-izq 3=abajo-der
                "score"             # puntuación en ese momento
            ])

def get_zone(x, y):
    """Divide el mapa en 4 zonas."""
    half = rows // 2
    if x < half and y < half: return 0   # arriba-izquierda
    if x >= half and y < half: return 1  # arriba-derecha
    if x < half and y >= half: return 2  # abajo-izquierda
    return 3                              # abajo-derecha

def save_row(x, y, direction, length, score):
    zone = get_zone(x, y)
    with open(CSV_FILE, "a", newline="") as f:
        csv.writer(f).writerow([x, y, direction, length, zone, score])

def count_data():
    if not os.path.exists(CSV_FILE):
        return 0
    with open(CSV_FILE) as f:
        return max(0, sum(1 for _ in f) - 1)


# ─── CLASE CUBE ──────────────────────────────────────────────
class cube():
    rows = 20
    w    = 500

    def __init__(self, start, dirnx=1, dirny=0, color=GREEN_BRIGHT):
        self.pos   = start
        self.dirnx = dirnx
        self.dirny = dirny
        self.color = color

    def move(self, dirnx, dirny):
        self.dirnx = dirnx
        self.dirny = dirny
        self.pos   = (self.pos[0] + self.dirnx, self.pos[1] + self.dirny)

    def draw(self, surface, eyes=False, index=0):
        dis = self.w // self.rows
        i, j = self.pos
        px, py = i * dis, j * dis
        if eyes:
            pygame.draw.rect(surface, HEAD_COLOR,  (px+1, py+1, dis-2, dis-2), border_radius=5)
            pygame.draw.rect(surface, WHITE,        (px+1, py+1, dis-2, dis-2), 2, border_radius=5)
            pygame.draw.circle(surface, BLACK, (px+6,     py+7), 3)
            pygame.draw.circle(surface, BLACK, (px+dis-7, py+7), 3)
        else:
            color = GREEN_BRIGHT if index % 2 == 0 else GREEN_DARK
            pygame.draw.rect(surface, color, (px+2, py+2, dis-4, dis-4), border_radius=4)


# ─── CLASE SNAKE ─────────────────────────────────────────────
class snake():
    def __init__(self, color, pos):
        self.color     = color
        self.head      = cube(pos)
        self.body      = [self.head]
        self.turns     = {}
        self.dirnx     = 0
        self.dirny     = 1
        self.last_dir  = 1   # 0=arr 1=abj 2=izq 3=der

    def move(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            keys = pygame.key.get_pressed()
            for key in keys:
                if keys[pygame.K_LEFT]  and self.dirnx != 1:
                    self.dirnx, self.dirny = -1,  0
                    self.last_dir = 2
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
                elif keys[pygame.K_RIGHT] and self.dirnx != -1:
                    self.dirnx, self.dirny =  1,  0
                    self.last_dir = 3
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
                elif keys[pygame.K_UP]    and self.dirny != 1:
                    self.dirnx, self.dirny =  0, -1
                    self.last_dir = 0
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
                elif keys[pygame.K_DOWN]  and self.dirny != -1:
                    self.dirnx, self.dirny =  0,  1
                    self.last_dir = 1
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

        for i, c in enumerate(self.body):
            p = c.pos[:]
            if p in self.turns:
                turn = self.turns[p]
                c.move(turn[0], turn[1])
                if i == len(self.body) - 1:
                    self.turns.pop(p)
            else:
                c.move(c.dirnx, c.dirny)

    def reset(self, pos):
        self.head  = cube(pos)
        self.body  = [self.head]
        self.turns = {}
        self.dirnx = 0
        self.dirny = 1

    def addCube(self):
        tail   = self.body[-1]
        dx, dy = tail.dirnx, tail.dirny
        if   dx ==  1 and dy == 0: self.body.append(cube((tail.pos[0]-1, tail.pos[1])))
        elif dx == -1 and dy == 0: self.body.append(cube((tail.pos[0]+1, tail.pos[1])))
        elif dx == 0  and dy == 1: self.body.append(cube((tail.pos[0],   tail.pos[1]-1)))
        elif dx == 0  and dy ==-1: self.body.append(cube((tail.pos[0],   tail.pos[1]+1)))
        self.body[-1].dirnx = dx
        self.body[-1].dirny = dy

    def draw(self, surface):
        for i, c in enumerate(self.body):
            c.draw(surface, eyes=(i == 0), index=i)


# ─── OBSTÁCULOS ──────────────────────────────────────────────
def draw_obstacles(surface, obstacles):
    dis = width // rows
    for (ox, oy) in obstacles:
        px, py = ox * dis, oy * dis
        pygame.draw.rect(surface, OBSTACLE_COL,
                         (px+1, py+1, dis-2, dis-2), border_radius=4)
        pygame.draw.rect(surface, OBSTACLE_BRD,
                         (px+1, py+1, dis-2, dis-2), 2, border_radius=4)
        # X encima
        pygame.draw.line(surface, WHITE, (px+5, py+5), (px+dis-6, py+dis-6), 2)
        pygame.draw.line(surface, WHITE, (px+dis-6, py+5), (px+5, py+dis-6), 2)


# ─── DIBUJO ──────────────────────────────────────────────────
def draw_apple(surface, pos):
    dis    = width // rows
    px, py = pos[0] * dis, pos[1] * dis
    cx, cy = px + dis // 2, py + dis // 2
    r      = dis // 2 - 2
    pygame.draw.circle(surface, (120, 0, 0),    (cx+2, cy+2), r)
    pygame.draw.circle(surface, RED_APPLE,       (cx,   cy  ), r)
    pygame.draw.circle(surface, (255, 130, 130), (cx-3, cy-3), r//3)
    pygame.draw.line  (surface, (80, 50, 20),    (cx, cy-r), (cx+3, cy-r-5), 2)
    pygame.draw.ellipse(surface, (0, 180, 0),    (cx+2, cy-r-5, 7, 4))

def drawGrid(w, rows, surface):
    size = w // rows
    for l in range(rows):
        x = (l + 1) * size
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, w))
        pygame.draw.line(surface, GRID_COLOR, (0, x), (w, x))

def draw_hud(surface, score, data_count, obstacles_placed):
    # Score
    sc = font_score.render(f"Score: {score}", True, GREEN_BRIGHT)
    surface.blit(sc, (8, 6))

    # Datos acumulados
    dat = font_small.render(f"Datos: {data_count}", True, GRAY)
    surface.blit(dat, (8, 30))

    # Obstáculos colocados
    obs = font_small.render(f"Obstaculos IA: {obstacles_placed}", True, OBSTACLE_BRD)
    surface.blit(obs, (8, 46))

    # Próximo obstáculo
    next_at = ((score // 5) + 1) * 5
    nxt = font_small.render(f"Siguiente obstaculo en: {next_at} pts", True, YELLOW)
    surface.blit(nxt, (width - nxt.get_width() - 8, 6))

def draw_game_over(surface, score, data_count):
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 185))
    surface.blit(overlay, (0, 0))

    t = font_big.render("GAME OVER", True, RED_APPLE)
    surface.blit(t, (width//2 - t.get_width()//2, height//2 - 110))

    sc = font_medium.render(f"Puntuacion: {score}", True, WHITE)
    surface.blit(sc, (width//2 - sc.get_width()//2, height//2 - 45))

    d = font_medium.render(f"Datos totales: {data_count}", True, YELLOW)
    surface.blit(d, (width//2 - d.get_width()//2, height//2 - 5))

    # Mensaje según cantidad de datos
    if data_count < 200:
        msg, col = "Sigue jugando para mejorar la IA!", GRAY
    elif data_count < 600:
        msg, col = "La IA ya empieza a aprender tu estilo!", GREEN_BRIGHT
    else:
        msg, col = "La IA te conoce muy bien!", YELLOW

    m = font_small.render(msg, True, col)
    surface.blit(m, (width//2 - m.get_width()//2, height//2 + 35))

    r = font_medium.render("R = Reiniciar    Q = Salir", True, GRAY)
    surface.blit(r, (width//2 - r.get_width()//2, height//2 + 68))

def redrawWindow(win, score, data_count, obstacles, obstacles_placed, game_over=False):
    win.fill(BLACK)
    drawGrid(width, rows, win)
    draw_obstacles(win, obstacles)
    s.draw(win)
    draw_apple(win, snack.pos)
    draw_hud(win, score, data_count, obstacles_placed)
    if game_over:
        draw_game_over(win, score, data_count)
    pygame.display.update()

def randomSnack(rows, item, obstacles):
    positions = [c.pos for c in item.body]
    while True:
        x = random.randrange(1, rows - 1)
        y = random.randrange(1, rows - 1)
        if (x, y) not in positions and (x, y) not in obstacles:
            return (x, y)


# ─── LÓGICA DE OBSTÁCULOS (placeholder — aquí entrará la IA) ─
def place_obstacle_simple(position_history, obstacles, snake_body, snack_pos):
    """
    Por ahora coloca el obstáculo en la celda MÁS visitada
    que no esté ocupada. En el siguiente paso esto se
    reemplaza por GMM + KNN + K-Means.
    """
    if len(position_history) < 10:
        return obstacles

    # Contar frecuencia de posiciones
    freq = Counter(position_history)

    # Ordenar de más a menos visitada
    sorted_pos = [pos for pos, _ in freq.most_common()]

    snake_pos  = set(c.pos for c in snake_body)

    for candidate in sorted_pos:
        if (candidate not in obstacles and
            candidate not in snake_pos and
            candidate != snack_pos and
            1 <= candidate[0] <= rows-2 and
            1 <= candidate[1] <= rows-2):
            obstacles.add(candidate)
            return obstacles

    return obstacles


# ─── MAIN ────────────────────────────────────────────────────
def main():
    global s, snack, win
    init_csv()

    win = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Snake Adaptativo - IA observando...")

    s     = snake(GREEN_BRIGHT, (10, 10))
    s.addCube()

    obstacles = set()
    snack     = cube(randomSnack(rows, s, obstacles), color=RED_APPLE)

    clock             = pygame.time.Clock()
    score             = 0
    game_over         = False
    position_history  = []   # historial de posiciones visitadas
    last_obstacle_score = 0  # score en el que se colocó el último obstáculo
    obstacles_placed  = 0

    while True:
        pygame.time.delay(50)
        clock.tick(10)

        data_count = count_data()

        if game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        main(); return
                    if event.key == pygame.K_q:
                        pygame.quit(); return
            redrawWindow(win, score, data_count, obstacles, obstacles_placed, game_over=True)
            continue

        s.move()
        headPos = s.head.pos

        # ── Registrar posición en historial y CSV ──
        position_history.append(headPos)
        save_row(headPos[0], headPos[1], s.last_dir, len(s.body), score)

        # ── Colisión con paredes ──
        if headPos[0] >= rows or headPos[0] < 0 or headPos[1] >= rows or headPos[1] < 0:
            game_over = True
            continue

        # ── Colisión con obstáculos ──
        if headPos in obstacles:
            game_over = True
            continue

        # ── Come la manzana ──
        if s.body[0].pos == snack.pos:
            s.addCube()
            score += 1
            snack  = cube(randomSnack(rows, s, obstacles), color=RED_APPLE)

            # ── Cada 5 puntos la IA coloca un obstáculo ──
            if score % 5 == 0 and score > last_obstacle_score:
                obstacles = place_obstacle_simple(
                    position_history, obstacles, s.body, snack.pos)
                last_obstacle_score = score
                obstacles_placed   += 1

        # ── Colisión consigo misma ──
        for x in range(len(s.body)):
            if s.body[x].pos in list(map(lambda z: z.pos, s.body[x+1:])):
                game_over = True
                break

        redrawWindow(win, score, data_count, obstacles, obstacles_placed)

main()