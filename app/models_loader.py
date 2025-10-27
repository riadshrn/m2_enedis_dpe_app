# app/models_loader.py
import joblib
from pathlib import Path

MODELS_PATH = Path(__file__).resolve().parent.parent / "models" / "Compressed"

print("Chargement des modèles compressés...")

models = {
    "rf_dpe_sans_conso": joblib.load(MODELS_PATH / "rf_dpe_sans_conso_compressed.joblib"),
    "rf_dpe_avec_conso": joblib.load(MODELS_PATH / "rf_dpe_avec_conso_compressed.joblib"),
    "rf_conso_final": joblib.load(MODELS_PATH / "rf_conso_final_compressed.joblib"),
}

print("Modèles chargés avec succès.")
