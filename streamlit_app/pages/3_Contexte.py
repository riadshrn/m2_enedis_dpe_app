import os
import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from pathlib import Path
from utils.layout import render_sidebar, load_css

logo_path = Path(__file__).parent.parent / "assets" / "logo-removebg.png"
# ========= CONFIG & STYLES =========
st.set_page_config(
    page_title="Contexte des Données Logements",
    page_icon=logo_path,
    layout="wide"
)

# Charger les styles et la sidebar commune
load_css()
render_sidebar()


# === HEADER ===
st.markdown("""
<div class="main-header fade-in">
    <h1>Contexte des Données Logements – DPE Rhône (69)</h1>
    <p>Visualisez, Filtrez, éxportez les données</p>
</div>
""", unsafe_allow_html=True)
# ==================== PAGE ====================

def show():
    # ==================== CHARGEMENT DES DONNÉES ====================
    # API_URL = os.getenv("API_URL", "https://riadshrn-api-dpe-conso.hf.space/data/visualisation?page=1&size=50000")

    # try:
    #     with st.spinner("Chargement des données depuis l’API..."):
    #         response = requests.get(API_URL, timeout=60)
    #         if response.status_code == 200:
    #             data = response.json()
    #             df = pd.DataFrame(data["data"])
    #         else:
    #             st.warning(f" API non disponible ({response.status_code}), chargement local.")
    #             df = pd.read_csv("../data/df_adem_enedis_iris_69_sample.csv.gz", compression="gzip")
    # except Exception:
    #     st.warning(" API non disponible — chargement du fichier local d’échantillon.")
    #     df = pd.read_csv("../data/df_adem_enedis_iris_69_sample.csv.gz", compression="gzip")

    # if df.empty:
    #     st.error(" Aucune donnée trouvée.")
    #     return

    # ==================== CHARGEMENT DES DONNÉES ====================
    csv_path = Path(__file__).parent.parent / "data" / "df_adem_enedis_iris_69_prepared.csv.gz"

    try:
        with st.spinner("Chargement de 358302 logements via l'API ..."):
            df = pd.read_csv(csv_path, compression="gzip")
            st.success(f"Données chargées  — {len(df):,} lignes.")
    except Exception as e:
        st.error(f"Erreur lors du chargement du CSV local : {e}")

    if df.empty:
        st.error("Aucune donnée trouvée.")
        return

    # ==================== FILTRES ====================
    st.subheader("Filtres interactifs")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        commune = st.multiselect(" Commune", sorted(df["nom_commune_ban"].dropna().unique()))
    with col2:
        dpe_label = st.multiselect(" Étiquette DPE", sorted(df["etiquette_dpe"].dropna().unique()))
    with col3:
        energie = st.multiselect(" Énergie principale", sorted(df["type_energie_principale_chauffage"].dropna().unique()))
    with col4:
        zone_clim = st.multiselect(" Zone climatique", sorted(df["zone_climatique"].dropna().unique()))
    with col5:
        classe_annee = st.multiselect(" Classe année construction", sorted(df["classe_annee_construction"].dropna().unique()))

    filtered_df = df.copy()
    if commune:
        filtered_df = filtered_df[filtered_df["nom_commune_ban"].isin(commune)]
    if dpe_label:
        filtered_df = filtered_df[filtered_df["etiquette_dpe"].isin(dpe_label)]
    if energie:
        filtered_df = filtered_df[filtered_df["type_energie_principale_chauffage"].isin(energie)]
    if zone_clim:
        filtered_df = filtered_df[filtered_df["zone_climatique"].isin(zone_clim)]
    if classe_annee:
        filtered_df = filtered_df[filtered_df["classe_annee_construction"].isin(classe_annee)]

    # ==================== STATISTIQUES ====================
    st.subheader("Statistiques globales sur la sélection")

    total = len(filtered_df)
    mean_surface = filtered_df["surface_habitable_logement"].mean() if total > 0 else 0
    mean_conso = filtered_df["conso_m2"].mean() if total > 0 else 0
    mean_cout = filtered_df["cout_m2"].mean() if total > 0 else 0
    mean_age = filtered_df["anciennete"].mean() if total > 0 else 0

    # 🏷️ Classe DPE dominante
    if total > 0 and "etiquette_dpe" in filtered_df.columns:
        most_common_dpe = (
            filtered_df["etiquette_dpe"]
            .value_counts()
            .idxmax() if not filtered_df["etiquette_dpe"].isna().all() else None
        )
        # couleur correspondante si dispo
        color_map = (
            filtered_df.groupby("etiquette_dpe")["color_dpe"].first().to_dict()
            if "color_dpe" in filtered_df.columns else {}
        )
        color = color_map.get(most_common_dpe, "#999999")
    else:
        most_common_dpe, color = None, "#999999"

    # ==================== AFFICHAGE ====================
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Nombre de logements", f"{total:,}")
    with col2:
        st.metric("Surface moyenne", f"{mean_surface:.1f} m²")
    with col3:
        st.metric("Conso moyenne", f"{mean_conso:.1f} kWh/m²/an")
    with col4:
        st.metric("Ancienneté moyenne", f"{mean_age:.0f} ans")
    with col5:
        if most_common_dpe:
            st.markdown(
                f"""
                <div style='text-align:center;'>
                    <span style='font-size:0.9rem;'>Étiquette DPE dominante</span><br>
                    <span style='font-size:1.5rem; font-weight:bold; color:{color};'>
                        {most_common_dpe}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.metric("Étiquette dominante", "N/A")



    # ==================== EXPORT ====================
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 1]) 

    with col3:
        st.download_button(
            label="Télécharger les données filtrées (CSV)",
            data=filtered_df.to_csv(index=False).encode("utf-8"),
            file_name="donnees_filtrees_dpe.csv",
            mime="text/csv",
            use_container_width=True,  
        )

    # ==================== AFFICHAGE DU TABLEAU ====================
    st.subheader("Tableau des logements filtrés")
    st.dataframe(filtered_df, use_container_width=True, height=700)


# Permet d’exécuter directement la page localement
if __name__ == "__main__":
    st.set_page_config(layout="wide")
    show()
