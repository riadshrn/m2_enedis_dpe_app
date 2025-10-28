from fastapi import APIRouter, Query
import pandas as pd
import os
from pathlib import Path

router = APIRouter()

# On charge directement le fichier parquet préparé
DATA_PATH = Path(__file__).resolve().parents[1]/ "data" / "df_adem_enedis_iris_69_sample.csv.gz"
print(DATA_PATH)

def get_df():
    print(f"Chargement du fichier : {DATA_PATH}")
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Fichier introuvable : {DATA_PATH}")

    #cols = ["nom_commune_ban", "etiquette_dpe", "conso_m2", "cout_m2", "lon", "lat"]
    df_global = pd.read_csv(DATA_PATH)
    print(f"DataFrame chargé ({len(df_global):,} lignes, {df_global.shape[1]} colonnes)")
    return df_global


@router.get("/data/visualisation")
def get_data_visualisation(
    page: int = Query(1, ge=1, description="Numéro de la page (à partir de 1)"),
    size: int = Query(1000, ge=1, le=5000, description="Taille de page (nombre de lignes)")
):
    """
    Route paginée pour récupérer les données prêtes à la visualisation.
    Le DataFrame est déjà préparé (lon, lat, conso_m2, etc.)
    """
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    df = get_df()

    # Pagination
    total_rows = len(df)
    total_pages = (total_rows + size - 1) // size

    start = (page - 1) * size
    end = start + size
    paginated_df = df.iloc[start:end]

    return {
        "message": "Données récupérées avec succès",
        "page": page,
        "size": size,
        "total_pages": total_pages,
        "total_rows": total_rows,
        "data": paginated_df.to_dict(orient="records")
    }
