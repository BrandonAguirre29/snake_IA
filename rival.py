import random
import pygame
from config import ROWS

RIVAL_COLOR      = (220, 60,  60 )
RIVAL_DARK       = (140, 20,  20 )
RIVAL_HEAD_COLOR = (255, 100, 100)
WHITE            = (255, 255, 255)
BLACK            = (0,   0,   0  )

DIS = 500 // ROWS

# Cada cuántos ticks del juego se mueve el rival según su generación
# El rival siempre se mueve cada tick — misma velocidad que el jugador
SPEED_TABLE = {
    0: 1,   # primera generación: igual de rápido
    1: 1,   # segunda generación: igual (ya respawneó)
    2: 1,   # tercera+: igual (la dificultad extra viene del respawn, no velocidad)
}


class RivalCube:
    def __init__(self, pos, dirnx=0, dirny=0):
        self.pos   = pos
        self.dirnx = dirnx
        self.dirny = dirny

    def move(self, dirnx, dirny):
        self.dirnx = dirnx
        self.dirny = dirny
        self.pos   = (self.pos[0] + dirnx, self.pos[1] + dirny)

    def draw(self, surface, is_head=False, index=0):
        px, py = self.pos[0] * DIS, self.pos[1] * DIS
        if is_head:
            pygame.draw.rect(surface, RIVAL_HEAD_COLOR,
                             (px+1, py+1, DIS-2, DIS-2), border_radius=5)
            pygame.draw.rect(surface, WHITE,
                             (px+1, py+1, DIS-2, DIS-2), 2, border_radius=5)
            pygame.draw.circle(surface, BLACK, (px+6,     py+7), 3)
            pygame.draw.circle(surface, BLACK, (px+DIS-7, py+7), 3)
        else:
            color = RIVAL_COLOR if index % 2 == 0 else RIVAL_DARK
            pygame.draw.rect(surface, color,
                             (px+2, py+2, DIS-4, DIS-4), border_radius=4)


class Rival:
    def __init__(self, pos):
        self.spawn_pos  = pos
        self.generation = 0          # cuántas veces ha respawneado
        self.lives      = 3          # primera generación: 3 vidas
        self._init_body(pos)
        self.move_timer = 0

    # ── Inicialización ──────────────────────────────────────────
    def _init_body(self, pos):
        self.head  = RivalCube(pos, dirnx=0, dirny=-1)
        self.body  = [self.head]
        self.dirnx = 0
        self.dirny = -1
        # Cuerpo inicial de 3 segmentos
        for i in range(1, 3):
            c = RivalCube((pos[0], pos[1] + i), dirnx=0, dirny=-1)
            self.body.append(c)
        self.move_timer = 0

    @property
    def move_every(self):
        """Ticks entre movimientos según generación."""
        gen = min(self.generation, 2)
        return SPEED_TABLE[gen]

    # ── Vida del rival ──────────────────────────────────────────
    def lose_life(self):
        """Quita una vida. Retorna True si el rival murió del todo."""
        self.lives -= 1
        if self.lives <= 0:
            return True
        # Aún tiene vidas: se reinicia en el mismo lugar
        self._init_body(self.spawn_pos)
        return False

    def respawn(self):
        """Respawnea en nueva generación — más rápido, 1 sola vida."""
        self.generation += 1
        self.lives = 1
        self._init_body(self.spawn_pos)

    def reset(self, pos):
        """Reset completo (cambio de nivel)."""
        self.spawn_pos  = pos
        self.generation = 0
        self.lives      = 3
        self._init_body(pos)

    # ── Movimiento ──────────────────────────────────────────────
    def addCube(self):
        tail = self.body[-1]
        self.body.append(RivalCube(
            (tail.pos[0] - tail.dirnx, tail.pos[1] - tail.dirny),
            tail.dirnx, tail.dirny))

    def _bfs_direction(self, target, walls, snake_body):
        """Mejor paso hacia target evitando obstáculos (greedy Manhattan)."""
        sx, sy = self.head.pos
        tx, ty = target
        blocked = (walls |
                   {c.pos for c in self.body[1:]} |
                   {c.pos for c in snake_body})

        directions = [(0,-1),(0,1),(-1,0),(1,0)]
        random.shuffle(directions)

        best_dir  = None
        best_dist = float('inf')

        for dx, dy in directions:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= ROWS or ny < 0 or ny >= ROWS:
                continue
            if (nx, ny) in blocked:
                continue
            dist = abs(nx - tx) + abs(ny - ty)
            if dist < best_dist:
                best_dist = dist
                best_dir  = (dx, dy)

        return best_dir if best_dir else (self.dirnx, self.dirny)

    def update(self, score, snack_pos, player_body, walls, life_apple=None):
        """
        Lógica de movimiento:
        - Prioridad 1 (siempre): si hay manzana de vida extra, ir por ella
        - Prioridad 2 fase 4a (score <35): ir por la manzana normal
        - Prioridad 2 fase 4b (score >=35): perseguir al jugador
        """
        self.move_timer += 1
        if self.move_timer < self.move_every:
            return
        self.move_timer = 0

        # Elegir objetivo
        if life_apple is not None and self.lives < 3:
           target = life_apple
        elif score < 25:
            target = snack_pos
        else:
            target = player_body[0].pos

        dx, dy = self._bfs_direction(target, walls, player_body)
        self.dirnx = dx
        self.dirny = dy

        # Mover cuerpo de atrás hacia adelante
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].pos   = self.body[i-1].pos
            self.body[i].dirnx = self.body[i-1].dirnx
            self.body[i].dirny = self.body[i-1].dirny

        self.head.move(dx, dy)

    # ── Colisiones ──────────────────────────────────────────────
    def collides_with_player(self, player_body):
        """True si la cabeza del rival toca al jugador o viceversa."""
        rival_head  = self.head.pos
        player_head = player_body[0].pos
        rival_cells = {c.pos for c in self.body}
        return player_head in rival_cells or rival_head == player_head

    def is_dead(self, walls):
        """True si el rival chocó con pared o consigo mismo."""
        hx, hy = self.head.pos
        if hx < 0 or hx >= ROWS or hy < 0 or hy >= ROWS:
            return True
        if self.head.pos in walls:
            return True
        if self.head.pos in {c.pos for c in self.body[1:]}:
            return True
        return False

    # ── Dibujo ──────────────────────────────────────────────────
    def draw(self, surface):
        for i, c in enumerate(self.body):
            c.draw(surface, is_head=(i == 0), index=i)

    # ── Info para HUD ────────────────────────────────────────────
    @property
    def speed_label(self):
        if self.generation == 0:
            return "normal"
        elif self.generation == 1:
            return "rapido"
        else:
            return f"rapido x{self.generation}"
