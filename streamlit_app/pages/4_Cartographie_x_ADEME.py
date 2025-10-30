import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import numpy as np
from io import BytesIO
from pathlib import Path
from utils.layout import render_sidebar, load_css

# ========== CONFIG ==========
logo_path = Path(__file__).parent.parent / "assets" / "logo-removebg.png"
st.set_page_config(page_title="DPE ADEME par commune", page_icon=logo_path, layout="wide")

# Sidebar + CSS
load_css()
render_sidebar()

# ========== HEADER ==========
st.markdown("""
<div class="main-header fade-in">
  <h1>Recherche DPE par commune (ADEME)</h1>
  <p>Consultez les DPE neufs publiés par l’ADEME pour une commune donnée</p>
</div>
""", unsafe_allow_html=True)

# ========== CHARGEMENT DES COMMUNES ==========
csv_communes_path = Path(__file__).parent.parent / "data" / "communes_ademe_par_dep.csv"

try:
    communes_df = pd.read_csv(csv_communes_path)
    communes_df = communes_df.dropna().sort_values("nom_commune_ban").reset_index(drop=True)
    st.success(f"{len(communes_df):,} communes chargées depuis l'ADEME")
except Exception as e:
    st.error(f"Impossible de charger la liste des communes : {e}")
    st.stop()

# ========== SÉLECTION COMMUNE ==========
st.markdown("---")
st.subheader("Sélectionnez une commune")

commune_input = st.selectbox(
    "Choisissez une commune dans la liste :",
    communes_df["nom_commune_ban"].unique(),
    index=None,
    placeholder="Exemple : Lyon, Angers, Arcangues...",
    key="commune_selectbox"
)

# ========== FONCTION REQUÊTE ADEME ==========
def fetch_dpe_by_commune(nom_commune: str, limit: int = 10000, pages: int = 10):
    """
    Récupère les DPE récents depuis l'API ADEME pour une commune donnée (avec pagination).
    """
    base_url = "https://data.ademe.fr/data-fair/api/v1/datasets/dpe02neuf/lines"
    all_results = []

    for page in range(1, pages + 1):
        params = {
            "qs": f'nom_commune_ban:"{nom_commune}"',
            "size": min(limit, 1000),
            "page": page,
            "select": "nom_commune_ban,type_batiment,surface_habitable_logement,etiquette_dpe,_geopoint,conso_5_usages_par_m2_ep,cout_total_5_usages,surface_habitable_logement,code_postal_ban,date_reception_dpe",
            "format": "json",
        }
        r = requests.get(base_url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json().get("results", [])
        if not data:
            break
        all_results.extend(data)
        if len(data) < 1000:
            break

    return pd.json_normalize(all_results)


def preprocess_dpe_api(df_api: pd.DataFrame) -> pd.DataFrame:
    """Nettoie et enrichit les données issues de l'API ADEME."""
    if df_api.empty:
        return df_api

    # Extraire lat/lon depuis _geopoint
    if "_geopoint" in df_api.columns:
        coords = df_api["_geopoint"].str.split(",", expand=True)
        df_api["lat"] = coords[0].astype(float)
        df_api["lon"] = coords[1].astype(float)

    # Calculs dérivés
    df_api["conso_m2"] = df_api["conso_5_usages_par_m2_ep"]
    df_api["cout_m2"] = df_api["cout_total_5_usages"] / df_api["surface_habitable_logement"]

    # Mapping couleur DPE
    color_map = {
        "A": "#00FF00", "B": "#7FFF00", "C": "#FFFF00",
        "D": "#FFD700", "E": "#FFA500", "F": "#FF4500", "G": "#FF0000"
    }
    df_api["color_dpe"] = df_api["etiquette_dpe"].map(color_map).fillna("#999999")
    df_api["source"] = "ADEME"

    return df_api


def compute_center_zoom(df: pd.DataFrame):
    """Calcule un centre + zoom dynamique selon l’emprise lat/lon."""
    if df.empty or {"lat", "lon"}.difference(df.columns):
        return {"lat": 46.6, "lon": 2.5}, 6  # France par défaut

    lat_min, lat_max = df["lat"].min(), df["lat"].max()
    lon_min, lon_max = df["lon"].min(), df["lon"].max()
    center = {"lat": (lat_min + lat_max) / 2, "lon": (lon_min + lon_max) / 2}
    span = max(lat_max - lat_min, lon_max - lon_min)
    zoom = 13 if span < 0.02 else 10 if span < 0.5 else 8
    return center, zoom


# ========== REQUÊTE ADEME ==========
if commune_input:
    if st.button("Rechercher les DPE depuis l’ADEME", use_container_width=True):
        with st.spinner(f"Récupération des DPE pour {commune_input}..."):
            try:
                df_api = fetch_dpe_by_commune(commune_input)
                if df_api.empty:
                    st.warning("Aucune donnée trouvée pour cette commune.")
                else:
                    df_api = preprocess_dpe_api(df_api)
                    st.success(f"{len(df_api):,} logements récupérés via l’API ADEME")

                    nb_unique = df_api[["lat", "lon"]].drop_duplicates().shape[0]
                    st.caption(f"{nb_unique} coordonnées uniques sur {len(df_api)} logements.")

                    # Ajout du jitter pour lisibilité
                    df_api["lat_jitter"] = df_api["lat"] + np.random.uniform(-0.0005, 0.0005, size=len(df_api))
                    df_api["lon_jitter"] = df_api["lon"] + np.random.uniform(-0.0005, 0.0005, size=len(df_api))

                    # === CARTE ===
                    st.markdown(f"### 🗺️ Carte des logements ADEME ({commune_input})")
                    center, zoom = compute_center_zoom(df_api)
                    fig_api = px.scatter_mapbox(
                        df_api,
                        lat="lat_jitter", lon="lon_jitter",
                        color="etiquette_dpe",
                        color_discrete_map=dict(df_api.groupby("etiquette_dpe")["color_dpe"].first()),
                        hover_name="nom_commune_ban",
                        hover_data=["type_batiment", "surface_habitable_logement", "conso_m2", "cout_m2", "date_reception_dpe"],
                        height=600,
                        zoom=zoom,
                        title=f"DPE ADEME – {commune_input}"
                    )
                    fig_api.update_layout(
                        mapbox_style="open-street-map",
                        mapbox_center=center,
                        margin=dict(l=0, r=0, t=40, b=0),
                        hoverlabel=dict(bgcolor="white", font_size=12),
                        dragmode="zoom"
                    )
                    fig_api.update_traces(marker=dict(size=9, opacity=0.85))
                    st.plotly_chart(fig_api, use_container_width=True, config={"scrollZoom": True})

                    # === DONNÉES & EXPORTS ===
                    with st.expander("Voir les données ADEME brutes récupérées"):
                        st.dataframe(df_api, use_container_width=True, height=400)

                    st.markdown("---")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.download_button(
                            "Télécharger les données (CSV)",
                            data=df_api.to_csv(index=False).encode("utf-8"),
                            file_name=f"dpe_ademe_{commune_input}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    with c2:
                        buf = BytesIO()
                        fig_api.write_image(buf, format="png", scale=2)
                        st.download_button(
                            "Enregistrer la carte (PNG)",
                            data=buf.getvalue(),
                            file_name=f"carte_dpe_ademe_{commune_input}.png",
                            mime="image/png",
                            use_container_width=True
                        )

            except Exception as e:
                st.error(f"Erreur lors de la requête ADEME : {e}")
