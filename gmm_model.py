# ─── gmm_model.py ────────────────────────────────────────────
# Modelo GMM (Gaussian Mixture Model) para predecir zonas calientes.
#
# ORIGEN: gmm_model.py (Snake_IA)
#
# Bugs corregidos del original:
#   1. os.patch.exists → os.path.exists  (typo que crasheaba load_model)
#   2. Indentación de zona_mas_probable corregida (el original tenía
#      el cuerpo de la función sin indentar correctamente, causando
#      SyntaxError o IndentationError al importar)
#
# Sin cambios en la lógica.

import os
import numpy as np
from sklearn.mixture import GaussianMixture
import joblib
from heatmap_prep import load_grid

MODEL_FILE = "gmm_model.joblib"


def prepare_points_from_grid(grid):
    """
    Convierte la grilla de frecuencias en una lista de puntos
    donde cada celda (x, y) aparece tantas veces como visitas tuvo.
    El GMM aprende la distribución de movimiento del jugador.
    """
    rows, cols = grid.shape
    pts = []
    for y in range(rows):
        for x in range(cols):
            count = int(grid[y, x])
            if count > 0:
                pts.extend([[x, y]] * count)
    if len(pts) == 0:
        return np.empty((0, 2))
    return np.array(pts)


def train(n_components=4, random_state=0):
    """
    Entrena el GMM con los datos actuales del CSV y guarda el modelo.
    n_components=4 porque el mapa está dividido en 4 zonas.
    """
    grid = load_grid()
    X = prepare_points_from_grid(grid)
    if X.shape[0] < n_components:
        # Datos insuficientes: usar un solo componente como fallback
        gm = GaussianMixture(n_components=1, random_state=random_state)
    else:
        gm = GaussianMixture(n_components=n_components, random_state=random_state)
    gm.fit(X)
    joblib.dump(gm, MODEL_FILE)
    return gm


def load_model():
    """Carga el modelo entrenado desde disco. Devuelve None si no existe."""
    if os.path.exists(MODEL_FILE):   # CORREGIDO: era os.patch.exists
        return joblib.load(MODEL_FILE)
    return None


def zona_mas_probable(obstacles_set=None, snake_positions=None, snack_pos=None, rows=20):
    """
    Devuelve la celda (x, y) con mayor probabilidad según el GMM
    que no esté ocupada por un obstáculo, la serpiente o la manzana.
    Retorna None si el modelo no está entrenado todavía.
    """
    gm = load_model()
    if gm is None:
        return None

    # Calcular probabilidad del GMM para cada celda del mapa
    probs = {}
    for y in range(rows):
        for x in range(rows):
            sample = np.array([[x, y]])
            try:
                p = np.exp(gm.score_samples(sample))[0]
            except Exception:
                p = 0
            probs[(x, y)] = p

    # Ordenar de mayor a menor probabilidad
    sorted_cells = sorted(probs.items(), key=lambda kv: kv[1], reverse=True)

    snake_set    = set(snake_positions) if snake_positions else set()
    obstacles_set = set(obstacles_set) if obstacles_set else set()

    for (cell, _) in sorted_cells:
        if cell in obstacles_set:
            continue
        if cell in snake_set:
            continue
        if snack_pos and cell == tuple(snack_pos):
            continue
        x, y = cell
        if 1 <= x <= rows - 2 and 1 <= y <= rows - 2:
            return cell

    return None
