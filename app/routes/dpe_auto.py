# app/routes/dpe_auto.py
from fastapi import APIRouter
import pandas as pd
from app.models_loader import models
from app.schemas import BaseFeatures

router = APIRouter(prefix="/predict", tags=["DPE auto (avec conso prédite)"])

@router.post("/dpe_auto")
def predict_dpe_auto(features: BaseFeatures):
    df = pd.DataFrame([features.dict()])

    model_conso = models["rf_conso_final"]
    conso_predite = model_conso.predict(df)[0]

    df["conso_m2"] = conso_predite
    model_dpe = models["rf_dpe_avec_conso"]
    etiquette = model_dpe.predict(df)[0]

    proba = model_dpe.predict_proba(df).max()
    return {
        "conso_predite": round(float(conso_predite), 3),
        "etiquette_dpe": etiquette,
        "proba": round(float(proba), 3)
    }