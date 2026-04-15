# ─── datos.py ────────────────────────────────────────────────
# Manejo del CSV de entrenamiento para la IA.
#
# ORIGEN: data_collector.py (Snake_IA) + datos.py (Snake_modificado)
#
# Cambios respecto a data_collector.py original:
#   - Se agrega la columna "level" al CSV (viene de datos.py del modificado)
#   - save_row ahora recibe 'level' como argumento extra
#   - get_zone() se define aquí en vez de en Snake.py
#   - Validación de tipos con try/except (heredada de data_collector.py)

import csv
import os
from config import ROWS

CSV_FILE = "snake_data.csv"

# Encabezados — coinciden exactamente con heatmap_prep.py y kmeans_model.py
HEADER = ["x", "y", "dir", "length", "zone", "score", "level"]


def init_csv():
    """Crea el CSV con encabezados si no existe."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            csv.writer(f).writerow(HEADER)


def get_zone(x, y):
    """
    Divide el mapa en 4 zonas iguales.
    0 = arriba-izquierda   1 = arriba-derecha
    2 = abajo-izquierda    3 = abajo-derecha
    """
    half = ROWS // 2
    if x < half and y < half: return 0
    if x >= half and y < half: return 1
    if x < half and y >= half: return 2
    return 3


def save_row(x, y, direction, length, score, level):
    """
    Guarda una fila validada en el CSV.
    zone se calcula aquí automáticamente a partir de x, y.
    """
    zone = get_zone(x, y)
    # Validación defensiva heredada de data_collector.py
    try:
        row = [int(x), int(y), int(direction), int(length), int(zone), int(score), int(level)]
    except Exception:
        return   # fila corrupta: ignorar silenciosamente
    with open(CSV_FILE, "a", newline="") as f:
        csv.writer(f).writerow(row)


def count_data():
    """Retorna cuántas filas de datos hay en el CSV (sin contar el encabezado)."""
    if not os.path.exists(CSV_FILE):
        return 0
    with open(CSV_FILE) as f:
        return max(0, sum(1 for _ in f) - 1)
