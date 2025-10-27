# app/routes/dpe_avec_conso.py
from fastapi import APIRouter
import pandas as pd
from app.models_loader import models
from app.schemas import DpeAvecConsoFeatures

router = APIRouter(prefix="/predict", tags=["DPE avec conso"])

@router.post("/dpe_avec_conso")
def predict_dpe_avec_conso(features: DpeAvecConsoFeatures):
    df = pd.DataFrame([features.dict()])
    model = models["rf_dpe_avec_conso"]
    pred = model.predict(df)[0]
    proba = model.predict_proba(df).max()
    return {"etiquette_dpe": pred, "proba": round(float(proba), 3)}
