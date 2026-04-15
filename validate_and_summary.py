# ─── validate_and_summary.py ─────────────────────────────────
# Herramienta de diagnóstico: valida el CSV e imprime estadísticas.
#
# ORIGEN: validate_and_summary.py (Snake_IA)
#
# Cambios:
#   - CSV_FILE importado desde datos.py (consistencia)
#   - ROWS importado desde config.py (consistencia)
#   - Se corrigió el bug: la condición "if d not in (0,1,2,3)" estaba
#     duplicada dos veces seguidas en el original
#   - Se agrega conteo por level (columna nueva del proyecto modificado)
#   - Se corre validate() automáticamente al ejecutar el archivo

import csv
from collections import Counter
from config import ROWS
from datos import CSV_FILE


def validate():
    """
    Lee el CSV fila por fila y reporta:
      - Total de filas
      - Filas con datos inválidos
      - Distribución de posiciones por zona (0-3)
      - Distribución por nivel (1, 3, 4)
    """
    bad    = 0
    total  = 0
    zones  = Counter()
    levels = Counter()

    with open(CSV_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            total += 1
            try:
                x      = int(r["x"])
                y      = int(r["y"])
                d      = int(r["dir"])
                length = int(r["length"])
                zone   = int(r["zone"])

                if not (0 <= x < ROWS and 0 <= y < ROWS):
                    bad += 1
                if d not in (0, 1, 2, 3):   # CORREGIDO: era doble
                    bad += 1
                if length < 1:
                    bad += 1

                zones[zone] += 1

                # Columna level (puede no existir en CSVs viejos)
                if "level" in r:
                    levels[int(r["level"])] += 1

            except Exception:
                bad += 1

    print(f"Total filas      : {total}")
    print(f"Filas inválidas  : {bad}")
    print(f"Distribución zona: {dict(sorted(zones.items()))}")
    if levels:
        print(f"Distribución nivel: {dict(sorted(levels.items()))}")


if __name__ == "__main__":
    validate()
