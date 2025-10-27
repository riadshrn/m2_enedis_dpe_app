from fastapi import FastAPI
from routes import (
    dpe_sans_conso,
    dpe_avec_conso,
    conso,
    dpe_auto,
    interpretation
)

app = FastAPI(title="API DPE / Consommation ENEDIS")

app.include_router(dpe_sans_conso.router)
app.include_router(dpe_avec_conso.router)
app.include_router(conso.router)
app.include_router(dpe_auto.router)
app.include_router(interpretation.router)

@app.get("/")
def home():
    return {"message": "Bienvenue sur l’API DPE/Conso ENEDIS"}