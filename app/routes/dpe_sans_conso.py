# app/routes/dpe_sans_conso.py
from fastapi import APIRouter
import pandas as pd
from models_loader import models
from schemas import DpeSansConsoFeatures

router = APIRouter(prefix="/predict", tags=["DPE sans conso"])

@router.post("/dpe_sans_conso")
def predict_dpe_sans_conso(features: DpeSansConsoFeatures):
    df = pd.DataFrame([features.dict()])
    model = models["rf_dpe_sans_conso"]
    pred = model.predict(df)[0]
    proba = model.predict_proba(df).max()
    return {"etiquette_dpe": pred, "proba": round(float(proba), 3)}
