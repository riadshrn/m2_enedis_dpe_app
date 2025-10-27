# app/routes/conso.py
from fastapi import APIRouter
import pandas as pd
from app.models_loader import models
from app.schemas import BaseFeatures

router = APIRouter(prefix="/predict", tags=["Consommation"])

@router.post("/conso")
def predict_conso(features: BaseFeatures):
    df = pd.DataFrame([features.dict()])
    model = models["rf_conso_final"]
    pred = model.predict(df)[0]
    return {"conso_predite": round(float(pred), 3)}
