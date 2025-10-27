from fastapi import APIRouter
import pandas as pd
from models_loader import models
from schemas import ConsoFeatures  

router = APIRouter(prefix="/predict", tags=["DPE auto (avec conso prédite)"])

@router.post("/dpe_auto")
def predict_dpe_auto(features: ConsoFeatures):
    # Conversion en DataFrame
    df = pd.DataFrame([features.dict()])

    # Prédiction de la consommation spécifique (kWh/m²/an)
    model_conso = models["rf_conso_final"]
    conso_m2_predite = model_conso.predict(df)[0]

    # Calcul de la consommation totale (MWh/an)
    surface = features.surface_habitable_logement
    conso_totale_mwh = (conso_m2_predite * surface) / 1000

    # Ajout de la conso prédite dans le DF pour la prédiction DPE
    df["conso_m2"] = conso_m2_predite

    # Prédiction de l’étiquette DPE
    model_dpe = models["rf_dpe_avec_conso"]
    etiquette = model_dpe.predict(df)[0]

    # Certaines versions de RandomForest n’ont pas predict_proba
    proba = None
    if hasattr(model_dpe, "predict_proba"):
        proba = float(model_dpe.predict_proba(df).max())

    # ⑤ Réponse complète
    return {
        "surface_habitable_logement": round(float(surface), 2),
        "conso_m2_predite": round(float(conso_m2_predite), 3),
        "conso_totale_mwh": round(float(conso_totale_mwh), 3),
        "etiquette_dpe": etiquette,
        "proba": round(proba, 3) if proba else None,
        "unites": {
            "conso_m2_predite": "kWh/m²/an",
            "conso_totale_mwh": "MWh/an"
        }
    }