# app/routes/conso.py
from fastapi import APIRouter
import pandas as pd
from models_loader import models
from schemas import ConsoFeatures

router = APIRouter(prefix="/predict", tags=["Consommation"])

@router.post("/conso")
def predict_conso(features: ConsoFeatures):
    # Création du DataFrame pour la prédiction
    df = pd.DataFrame([features.dict()])

    # Chargement du modèle de consommation
    model = models["rf_conso_final"]

    # Prédiction de la consommation spécifique (kWh/m²/an)
    conso_m2_pred = model.predict(df)[0]

    # Calcul de la consommation totale annuelle (en MWh)
    surface = features.surface_habitable_logement
    conso_totale_mwh = (conso_m2_pred * surface) / 1000

    # Réponse complète
    return {
        "conso_m2_predite": round(float(conso_m2_pred), 3),
        "surface_habitable_logement": round(float(surface), 2),
        "conso_totale_mwh": round(float(conso_totale_mwh), 3),
        "unites": {
            "conso_m2_predite": "kWh/m²/an",
            "conso_totale_mwh": "MWh/an"
        }
    }
