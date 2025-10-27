from fastapi import APIRouter, HTTPException
from functools import lru_cache
import json

# ✅ on va lire la ressource depuis le package "app.data"
try:
    from importlib.resources import files  # Python 3.9+
except ImportError:
    # Compat Python <3.9 (pas ton cas ici)
    from importlib_resources import files  # type: ignore

router = APIRouter(prefix="/metadata", tags=["Metadata"])

# 🔒 Fallback embarqué si le fichier est illisible / verrouillé
FALLBACK_VALUE_LISTS = {
    "isolation_toiture": [
        "0.0",
        "1.0"
    ],
    "qualite_isolation_murs": [
        "BONNE",
        "INSUFFISANTE",
        "MOYENNE",
        "TRÈS BONNE"
    ],
    "qualite_isolation_menuiseries": [
        "BONNE",
        "INSUFFISANTE",
        "MOYENNE",
        "TRÈS BONNE"
    ],
    "type_energie_principale_chauffage": [
        "BOIS – BÛCHES",
        "BOIS – GRANULÉS (PELLETS) OU BRIQUETTES",
        "BOIS – PLAQUETTES D’INDUSTRIE",
        "BOIS – PLAQUETTES FORESTIÈRES",
        "CHARBON",
        "FIOUL DOMESTIQUE",
        "GAZ NATUREL",
        "GPL",
        "PROPANE",
        "RÉSEAU DE CHAUFFAGE URBAIN",
        "ÉLECTRICITÉ",
        "ÉLECTRICITÉ D'ORIGINE RENOUVELABLE UTILISÉE DANS LE BÂTIMENT"
    ],
    "energie_regroupee": [
        "autre",
        "bois",
        "electrique",
        "fioul",
        "gaz"
    ],
    "type_logement_source": [
        "EXISTANT",
        "NEUF"
    ],
    "classe_annee_construction": [
        "1949_1974",
        "1975_1989",
        "1990_1999",
        "2000_2011",
        "apres_2012",
        "avant_1948"
    ]
}

@lru_cache()
def load_value_lists() -> dict:
    """
    Charge app/data/value_lists.json depuis le package.
    Si le fichier est introuvable ou illisible, renvoie les valeurs de FALLBACK_VALUE_LISTS.
    """
    try:
        resource = files("app.data").joinpath("value_lists.json")
        text = resource.read_text(encoding="utf-8")
        return json.loads(text)
    except Exception as e:
        # Log utile en dev, mais on renvoie un fallback pour que l’UI continue de fonctionner
        print(f"[metadata] WARNING: impossible de lire value_lists.json ({e}). Fallback utilisé.")
        return FALLBACK_VALUE_LISTS

@router.get("/options")
def get_all_options():
    return load_value_lists()

@router.get("/options/{key}")
def get_options_for(key: str):
    lists = load_value_lists()
    if key not in lists:
        raise HTTPException(status_code=404, detail=f"Clé inconnue: {key}")
    return {key: lists[key]}
