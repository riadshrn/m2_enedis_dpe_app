from typing import List
from fastapi import APIRouter, Query
import pandas as pd
from pathlib import Path

router = APIRouter()

#DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "df_adem_enedis_iris_69_prepared.csv.gz"
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "df_adem_enedis_iris_69_sample.csv.gz"

print(f"[INFO] Fichier de données : {DATA_PATH}")

def get_df():
    """Charge le DataFrame CSV GZ depuis le chemin défini."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"❌ Fichier introuvable : {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    print(f"✅ DataFrame chargé ({len(df):,} lignes, {df.shape[1]} colonnes)")
    return df


# ==================== ROUTE 1 : VISUALISATION ====================
@router.get("/data/visualisation")
def get_data_visualisation(
    page: int = Query(1, ge=1, description="Numéro de la page (à partir de 1)"),
    size: int = Query(1000, ge=1, le=5000, description="Taille de page (nombre de lignes)")
):
    """
    Route paginée pour récupérer les données prêtes à la visualisation.
    """
    print(" Requête /data/visualisation reçue")
    df = get_df()

    # Pagination
    total_rows = len(df)
    total_pages = (total_rows + size - 1) // size
    start = (page - 1) * size
    end = start + size
    paginated_df = df.iloc[start:end]

    return {
        "message": " Données récupérées avec succès",
        "page": page,
        "size": size,
        "total_pages": total_pages,
        "total_rows": total_rows,
        "data": paginated_df.to_dict(orient="records")
    }


# ==================== ROUTE 2 : SELECT (colonnes spécifiques) ====================
@router.get("/data/select")
def get_data_select(
    columns: List[str] = Query(..., description="Colonnes à inclure dans la réponse"),
    page: int = Query(1, ge=1, description="Numéro de page"),
    size: int = Query(10000, ge=1, le=50000, description="Nombre de lignes par page")
):
    """
    Route flexible : permet de sélectionner uniquement certaines colonnes.
    Exemple :
       /data/select?columns=lat&columns=lon&columns=conso_m2&page=1&size=10000
    """
    print(f"📊 Requête /data/select reçue pour colonnes : {columns}")
    df = get_df()

    # Vérification des colonnes demandées
    all_cols = set(df.columns)
    requested = [c for c in columns if c in all_cols]
    missing = [c for c in columns if c not in all_cols]

    if not requested:
        return {
            "error": "Aucune colonne valide trouvée",
            "available_columns": list(all_cols)
        }

    # Sous-ensemble du DataFrame
    df = df[requested]

    # Pagination
    total_rows = len(df)
    total_pages = (total_rows + size - 1) // size
    start = (page - 1) * size
    end = start + size
    paginated_df = df.iloc[start:end]

    return {
        "message": "Données filtrées avec succès",
        "requested_columns": requested,
        "missing_columns": missing,
        "page": page,
        "size": size,
        "total_rows": total_rows,
        "total_pages": total_pages,
        "data": paginated_df.to_dict(orient="records")
    }

@router.get("/data/detail/{id}")
def get_logement_detail(id: int):
    """
    Renvoie toutes les informations d’un logement spécifique, selon son index dans le DataFrame.
    """
    df = get_df()

    if id < 0 or id >= len(df):
        return {
            "error": "Index hors limites",
            "max_index": len(df) - 1
        }

    record = df.iloc[id].to_dict()
    return {
        "message": f"Détails du logement #{id}",
        "columns": list(record.keys()),
        "logement": record
    }
