# ─── niveles.py ──────────────────────────────────────────────
# Configuración de niveles, paredes, spawn y lógica de obstáculos IA.
#
# place_obstacle tiene DOS modos:
#   Modo 1 — GMM (si el modelo está entrenado):
#       Usa gmm_model.zona_mas_probable() para elegir la celda según
#       la distribución aprendida de TODAS las partidas anteriores.
#   Modo 2 — Counter (siempre disponible como fallback):
#       Coloca el obstáculo en la celda más visitada del historial
#       de esta partida. Siempre funciona aunque no haya modelo.
#
# La zona de seguridad Manhattan evita poner obstáculos a ≤4 celdas
# de la cabeza actual, dándole al jugador tiempo de reaccionar.

import random
from collections import Counter
from config import ROWS

# ── Área jugable por nivel ──
PLAY_AREA = {
    1: (1, ROWS-1, 1, ROWS-1),
    2: (3, 17,     3, 17    ),
    3: (1, ROWS-1, 1, ROWS-1),
}

# ── Paredes fijas por nivel ──
# Nivel 2 eliminado. Nivel 3 mantiene su borde interior.
LEVEL_WALLS = {
    1: [],

    2: [
        # Borde superior
        (2,2),(3,2),(4,2),(5,2),(6,2),(7,2),(8,2),(9,2),
        (10,2),(11,2),(12,2),(13,2),(14,2),(15,2),(16,2),(17,2),
        # Borde inferior
        (2,17),(3,17),(4,17),(5,17),(6,17),(7,17),(8,17),(9,17),
        (10,17),(11,17),(12,17),(13,17),(14,17),(15,17),(16,17),(17,17),
        # Borde izquierdo
        (2,3),(2,4),(2,5),(2,6),(2,7),(2,8),(2,9),
        (2,10),(2,11),(2,12),(2,13),(2,14),(2,15),(2,16),
        # Borde derecho
        (17,3),(17,4),(17,5),(17,6),(17,7),(17,8),(17,9),
        (17,10),(17,11),(17,12),(17,13),(17,14),(17,15),(17,16),
    ],

    3: [],
}

# ── Umbrales de cambio de nivel ──
# Nivel 1 dura 10 manzanas para que la IA recolecte datos antes de poner obstáculos.
# Nivel 2 (antes "3") empieza en 10, nivel 3 en 20, victoria en 30.
LEVEL_THRESHOLDS = {
    1:  0,   # empieza aquí
    2: 10,   # sube a nivel 2 al llegar a 10
    3: 20,   # sube a nivel 3 al llegar a 20
}
SCORE_WIN = 30


def get_level(score):
    if score < LEVEL_THRESHOLDS[2]: return 1
    if score < LEVEL_THRESHOLDS[3]: return 2
    return 3


def get_walls(level):
    return set(map(tuple, LEVEL_WALLS.get(level, [])))


def find_safe_spawn(walls, level=1):
    xmin, xmax, ymin, ymax = PLAY_AREA.get(level, (1, ROWS-1, 1, ROWS-1))
    candidates = [
        (10,10),(10,5),(5,5),(15,5),(5,15),(15,15),
        (7,7),(12,7),(7,12),(12,12),
        (10,7),(7,10),(10,13),(13,10),
        (3,3),(16,3),(3,16),(16,16),
    ]
    for pos in candidates:
        x, y = pos
        if not (xmin <= x < xmax and ymin <= y < ymax):
            continue
        if pos in walls:
            continue
        neighbors = [(x,y-1),(x,y+1),(x-1,y),(x+1,y)]
        if all(n not in walls for n in neighbors):
            return pos
    for x in range(xmin, xmax):
        for y in range(ymin, ymax):
            if (x, y) not in walls:
                return (x, y)
    return (xmin, ymin)


def randomSnack(snake_body, blocked, exclude=None, level=1):
    """Posición libre DENTRO del área jugable del nivel."""
    positions = [c.pos for c in snake_body]
    exclude   = exclude or set()
    xmin, xmax, ymin, ymax = PLAY_AREA.get(level, (1, ROWS-1, 1, ROWS-1))
    attempts  = 0
    while True:
        x = random.randrange(xmin, xmax)
        y = random.randrange(ymin, ymax)
        if ((x, y) not in positions and
            (x, y) not in blocked and
            (x, y) not in exclude):
            return (x, y)
        attempts += 1
        if attempts > 500:
            for fx in range(xmin, xmax):
                for fy in range(ymin, ymax):
                    if ((fx,fy) not in positions and
                        (fx,fy) not in blocked and
                        (fx,fy) not in exclude):
                        return (fx, fy)
            return (xmin, ymin)


def place_obstacle(position_history, obstacles, snake_body, snack_pos, walls, level=1):
    """
    Decide dónde colocar el próximo obstáculo usando la IA.

    Intenta primero con el GMM entrenado (gmm_model.py).
    Si el modelo no existe todavía, usa el Counter del historial
    de posiciones de esta partida como fallback.

    En ambos casos:
      - Respeta el área jugable del nivel actual.
      - Aplica zona de seguridad Manhattan (distancia > 4 a la cabeza).
    """
    if len(position_history) < 10:
        return obstacles   # muy pocos datos, no colocar nada aún

    head_pos = snake_body[0].pos
    xmin, xmax, ymin, ymax = PLAY_AREA.get(level, (1, ROWS-1, 1, ROWS-1))
    blocked = set(c.pos for c in snake_body) | walls

    def es_valido(candidate):
        cx, cy = candidate
        dist = abs(cx - head_pos[0]) + abs(cy - head_pos[1])
        return (candidate not in obstacles and
                candidate not in blocked and
                candidate != snack_pos and
                dist > 4 and
                xmin <= cx < xmax and
                ymin <= cy < ymax)

    # ── Intento 1: GMM ──────────────────────────────────────────
    # Solo se activa si el modelo ya fue entrenado (.joblib existe).
    try:
        from gmm_model import zona_mas_probable
        candidate = zona_mas_probable(
            obstacles_set=obstacles,
            snake_positions=[c.pos for c in snake_body],
            snack_pos=snack_pos,
            rows=ROWS
        )
        if candidate is not None and es_valido(candidate):
            obstacles.add(candidate)
            return obstacles
    except Exception:
        pass   # modelo no disponible → caer al Counter

    # ── Intento 2: Counter (método original Snake_IA) ───────────
    freq = Counter(position_history)
    for candidate, _ in freq.most_common():
        if es_valido(candidate):
            obstacles.add(candidate)
            return obstacles

    return obstacles
