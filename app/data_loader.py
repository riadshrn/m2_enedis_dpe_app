import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "conso_communes_rhone.csv"

print("Chargement des données communales du Rhône...")
df_communes = pd.read_csv(DATA_PATH)
print(f"Données chargées : {len(df_communes)} communes disponibles.")
