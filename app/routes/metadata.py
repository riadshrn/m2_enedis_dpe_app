from fastapi import APIRouter, HTTPException
from functools import lru_cache
import json
from pathlib import Path
import pandas as pd


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


# === Communes du Rhône ===
COMMUNES_PATH = Path(__file__).resolve().parents[1] / "data" / "conso_communes_rhone.csv"

@lru_cache()
def load_communes_df() -> pd.DataFrame:
    """
    Charge le fichier des communes du Rhône en mémoire (cache ldf pour accélérer les requêtes).
    """
    if not COMMUNES_PATH.exists():
        raise FileNotFoundError(f"Fichier introuvable: {COMMUNES_PATH}")
    df = pd.read_csv(COMMUNES_PATH, dtype=str)
    # Normalisation
    df.columns = [c.lower().strip() for c in df.columns]
    if "nom_commune" not in df.columns:
        raise ValueError("La colonne 'nom_commune' est manquante dans le CSV.")
    df["nom_commune_norm"] = df["nom_commune"].str.strip().str.lower()
    return df

@router.get("/communes")
def get_communes(search: str = None, limit: int = 15):
    """
    Renvoie la liste des communes du Rhône (auto-complétion facultative).
    - search: texte à chercher (insensible à la casse)
    - limit: nombre max de résultats
    """
    try:
        df = load_communes_df()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de lecture du fichier communes : {e}")

    if search:
        search_norm = search.strip().lower()
        mask = df["nom_commune_norm"].str.contains(search_norm, na=False)
        results = df.loc[mask, "nom_commune"].head(limit).tolist()
    else:
        results = df["nom_commune"].head(limit).tolist()

    return {"count": len(results), "communes": results}