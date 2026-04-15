# ─── kmeans_model.py ─────────────────────────────────────────
# Modelo K-Means para clasificar estilos de juego por partida.
#
# ORIGEN: kmeans_model.py (Snake_IA) — sin cambios funcionales.
#
# Cambios mínimos:
#   - CSV_FILE ahora se importa desde datos.py para consistencia.
#   - Se corrigió la importación (el original no tenía import de datos).

import numpy as np
from sklearn.cluster import KMeans
import joblib
import csv
from datos import CSV_FILE

MODEL_FILE = "kmeans_model.joblib"

# Cuántos ticks por "ventana" de análisis.
# Con FPS=10 y delay=50ms, el juego corre a ~10 ticks/seg.
# WINDOW=500 ≈ 50 segundos de juego por muestra.
WINDOW = 500


def extract_features_per_game(rows=20):
    """
    Lee el CSV y agrupa los datos en ventanas de WINDOW ticks.
    Por cada ventana calcula 2 features:
      - prop_center: qué tanto tiempo pasó el jugador en el centro del mapa
      - var_dir:     varianza de dirección (jugador impredecible vs rutinario)
    Devuelve un array (N_ventanas, 2).
    """
    feats = []
    with open(CSV_FILE, newline="") as f:
        reader = csv.DictReader(f)
        batch = []
        for r in reader:
            if isinstance(r, dict):
                batch.append(r)
            if len(batch) >= WINDOW:
                feat = _features_from_batch(batch, rows)
                if feat is not None:
                    feats.append(feat)
                batch = []
        # Procesar el último batch aunque sea más corto
        if batch:
            feat = _features_from_batch(batch, rows)
            if feat is not None:
                feats.append(feat)

    if len(feats) == 0:
        return np.empty((0, 2))
    return np.array(feats)


def _features_from_batch(batch, rows):
    """
    Convierte un batch (lista de dicts) en un vector [prop_center, var_dir].
    Ignora filas corruptas de forma segura.
    """
    try:
        xs, ys, dirs = [], [], []
        for r in batch:
            if not isinstance(r, dict):
                continue
            try:
                xs.append(int(r.get("x", 0)))
                ys.append(int(r.get("y", 0)))
                dirs.append(int(r.get("dir", 0)))
            except Exception:
                continue   # fila corrupta: saltar

        if len(xs) == 0:
            return None

        # Proporción de tiempo en el tercio central del mapa
        cx_min = rows // 3
        cx_max = rows - rows // 3
        center_count = sum(
            1 for x, y in zip(xs, ys)
            if cx_min <= x < cx_max and cx_min <= y < cx_max
        )
        prop_center = center_count / max(1, len(xs))

        # Varianza de dirección: alta = jugador errático, baja = jugador lineal
        var_dir = float(np.var(dirs)) if dirs else 0.0

        return [prop_center, var_dir]
    except Exception:
        return None


def train(n_clusters=3, random_state=0):
    """
    Entrena el K-Means con los features extraídos del CSV.
    n_clusters=3: jugador de centro, jugador de bordes, jugador mixto.
    """
    X = extract_features_per_game()
    if X.shape[0] < n_clusters:
        print(f"[KMeans] Datos insuficientes ({X.shape[0]} muestras). Necesita al menos {n_clusters}.")
        return None
    km = KMeans(n_clusters=n_clusters, random_state=random_state, n_init="auto")
    km.fit(X)
    joblib.dump(km, MODEL_FILE)
    return km
