# ─── heatmap_prep.py ─────────────────────────────────────────
# Construye una grilla de frecuencias de visitas a partir del CSV.
#
# ORIGEN: heatmap_prep.py (Snake_IA) — sin cambios funcionales.
#
# Cambios mínimos:
#   - CSV_FILE y ROWS ahora se importan desde datos.py y config.py
#     para que todo el proyecto use las mismas constantes.
#   - Se eliminó la redefinición local de CSV_FILE = "snake_data.csv"

import csv
import numpy as np
from config import ROWS
from datos import CSV_FILE


def load_grid():
    """
    Lee el CSV y devuelve una matriz (ROWS x ROWS) donde cada celda
    contiene cuántas veces la cabeza de la serpiente pasó por ahí.
    Esta grilla es la entrada principal para el modelo GMM.
    """
    grid = np.zeros((ROWS, ROWS), dtype=int)
    with open(CSV_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            try:
                x = int(r["x"])
                y = int(r["y"])
                if 0 <= x < ROWS and 0 <= y < ROWS:
                    grid[y, x] += 1   # fila = y, columna = x
            except Exception:
                continue
    return grid


if __name__ == "__main__":
    g = load_grid()
    print("Grid shape:", g.shape)
    print("Max visitas en una celda:", g.max())
