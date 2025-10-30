# pages/5_Dashboard_DPE.py
import os
import time
from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from utils.layout import render_sidebar, load_css

# Charger les styles et la sidebar commune
load_css()
render_sidebar()

logo_path = Path(__file__).parent.parent / "assets" / "logo-removebg.png"
# ========= CONFIG & STYLES =========
st.set_page_config(
    page_title="Dashboard DPE – Rhône (69)",
    page_icon=logo_path,
    layout="wide"
)

st.markdown("""
<div class="main-header fade-in">
  <h1>Dashboard efficacité énergétique – Rhône (69)</h1>
  <p>KPIs, graphiques et carte choroplèthe filtrables (données locales CSV)</p>
</div>
""", unsafe_allow_html=True)


# ==================== CHARGEMENT DES DONNÉES ====================
csv_path = Path(__file__).parent.parent / "data" / "df_adem_enedis_iris_69_prepared.csv.gz"

with st.spinner("Chargement de 358302 logements ..."):
    df = pd.read_csv(csv_path, compression="gzip")
    if "row_id" not in df.columns:
        df = df.reset_index(names="row_id")


# ========= FILTRES GLOBAUX =========
st.markdown("### Filtres")

with st.container():
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        communes = sorted(df["nom_commune_ban"].dropna().unique().tolist())
        commune_sel = st.multiselect("Commune", communes)
    with c2:
        types_bat = sorted(df["type_batiment"].dropna().unique().tolist())
        type_bat_sel = st.multiselect("Type de bâtiment", types_bat)
    with c3:
        etiquettes = ["A","B","C","D","E","F","G"]
        etiquettes_sel = st.multiselect("Étiquette DPE", etiquettes)
    with c4:
        classes_annee = [x for x in df["classe_annee_construction"].dropna().unique().tolist() if isinstance(x, str)]
        classes_annee = sorted(classes_annee)
        classe_annee_sel = st.multiselect("Classe année construction", classes_annee)
    with c5:
        energies = sorted(df["type_energie_principale_chauffage"].dropna().unique().tolist())
        energie_sel = st.multiselect("Type d’énergie principale", energies)


    n1, n2, n3 = st.columns(3)
    with n1:
        surf_min, surf_max = int(df["surface_habitable_logement"].min(skipna=True) or 0), int(df["surface_habitable_logement"].max(skipna=True) or 200)
        surface_range = st.slider("Surface habitable (m²)", max(10, surf_min), max(20, surf_max), (max(10, surf_min), min(200, surf_max)))
    with n2:
        conso_min, conso_max = int(np.nanmin(df["conso_m2"])), int(np.nanmax(df["conso_m2"]))
        conso_range = st.slider("Consommation (kWh/m²/an)", max(0, conso_min), max(50, conso_max), (max(0, conso_min), min(300, conso_max)))
    with n3:
        cout_min, cout_max = int(np.nanmin(df["cout_m2"])), int(np.nanmax(df["cout_m2"]))
        cout_range = st.slider("Coût (€/m²/an)", max(0, cout_min), max(50, cout_max), (max(0, cout_min), int(min(200, cout_max))))

# Appliquer les filtres
filtered = df.copy()
if commune_sel:
    filtered = filtered[filtered["nom_commune_ban"].isin(commune_sel)]
if type_bat_sel:
    filtered = filtered[filtered["type_batiment"].isin(type_bat_sel)]
if etiquettes_sel:
    filtered = filtered[filtered["etiquette_dpe"].isin(etiquettes_sel)]
if classe_annee_sel:
    filtered = filtered[filtered["classe_annee_construction"].isin(classe_annee_sel)]
if energie_sel:
    filtered = filtered[filtered["type_energie_principale_chauffage"].isin(energie_sel)]

filtered = filtered[
    filtered["surface_habitable_logement"].between(*surface_range)
    & filtered["conso_m2"].between(*conso_range)
    & filtered["cout_m2"].between(*cout_range)
]

#st.info(f"**Sélection** : {len(filtered):,} logements (sur {len(df):,})")


# ========= KPI =========
st.markdown("#### Indicateurs clés")
k1, k2, k3, k4 = st.columns(4)

def metric_card(title, value):
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #003366 0%, #33CC33 100%);
        padding: 0.1rem;
        border-radius: 12px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    ">
        <h3 style="margin:0; font-size:1rem; opacity:0.9;">{title}</h3>
        <h2 style="margin-top:0.3rem; font-size:1.8rem;">{value}</h2>
    </div>
    """, unsafe_allow_html=True)

with k1:
    metric_card("Logements", f"{len(filtered):,}/{len(df):,}")

with k2:
    moy_conso = filtered["conso_m2"].mean()
    metric_card("Conso moyenne (kWh/m²/an)", f"{moy_conso:.1f}" if pd.notna(moy_conso) else "—")

with k3:
    moy_cout = filtered["cout_m2"].mean()
    metric_card("Coût moyen (€/m²/an)", f"{moy_cout:.1f}" if pd.notna(moy_cout) else "—")

with k4:
    moy_ges = filtered["emission_ges_5_usages"].mean()
    metric_card("GES moyen (kgCO₂e/an)", f"{moy_ges:.1f}" if pd.notna(moy_ges) else "—")



# ========= OUTILS COMMUNS VISU =========
# Couleurs par étiquette (depuis la colonne color_dpe lorsqu’on agrège)
dpe_color_map = (
    filtered.dropna(subset=["etiquette_dpe", "color_dpe"])
    .groupby("etiquette_dpe")["color_dpe"].first().to_dict()
)
# Valeurs par défaut si besoin
dpe_color_map = {
    **{"A": "#00FF00","B": "#7FFF00","C": "#FFFF00","D": "#FFD700","E": "#FFA500","F": "#FF4500","G": "#FF0000"},
    **dpe_color_map
}


# ========= FABRIQUE À GRAPHIQUES =========
def fig_repartition_dpe(df_):
    if df_.empty:
        return None
    tmp = (
        df_[["etiquette_dpe", "color_dpe"]]
        .value_counts("etiquette_dpe")
        .rename("count")
        .reset_index()
    )
    tmp["color"] = tmp["etiquette_dpe"].map(dpe_color_map)
    fig = px.bar(
        tmp.sort_values("etiquette_dpe"),
        x="etiquette_dpe", y="count",
        title="Répartition par étiquette DPE",
        text="count"
    )
    fig.update_traces(marker_color=tmp.sort_values("etiquette_dpe")["color"])
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    return fig

def fig_conso_par_type_bat(df_):
    if df_.empty:
        return None
    tmp = df_.groupby("type_batiment", as_index=False)["conso_m2"].mean().sort_values("conso_m2")
    return px.bar(tmp, x="conso_m2", y="type_batiment", orientation="h",
                  title="Conso moyenne par type de bâtiment",
                  labels={"conso_m2":"kWh/m²/an", "type_batiment":"Type de bâtiment"})

def fig_cout_par_commune(df_):
    if df_.empty:
        return None
    tmp = df_.groupby("nom_commune_ban", as_index=False)["cout_m2"].mean().sort_values("cout_m2", ascending=False).head(25)
    return px.bar(tmp, x="nom_commune_ban", y="cout_m2",
                  title="Top 25 – Coût moyen par commune (€/m²/an)")

def fig_hist_conso(df_):
    if df_.empty:
        return None
    return px.histogram(df_, x="conso_m2", nbins=40, title="Distribution de la consommation (kWh/m²/an)")

def fig_box_cout_par_dpe(df_):
    if df_.empty:
        return None
    fig = px.box(df_, x="etiquette_dpe", y="cout_m2", title="Coût (€/m²/an) par étiquette DPE",color="etiquette_dpe",color_discrete_map=dpe_color_map)
    #fig.update_traces(marker_color=df_["etiquette_dpe"].map(dpe_color_map))
    return fig

def fig_dpe_par_zone(df_):
    if df_.empty:
        return None
    tmp = df_.groupby(["zone_climatique","etiquette_dpe"], as_index=False).size().rename(columns={"size":"count"})
    fig = px.bar(tmp, x="zone_climatique", y="count", color="etiquette_dpe",
                 title="Répartition DPE par zone climatique", barmode="stack",
                 color_discrete_map=dpe_color_map)
    return fig

def fig_energie_pie(df_):
    if df_.empty:
        return None
    tmp = df_["type_energie_principale_chauffage"].fillna("INCONNU").value_counts().reset_index()
    tmp.columns = ["énergie", "count"]
    return px.pie(tmp, names="énergie", values="count", title="Répartition des énergies principales")

def fig_isolation_vs_conso(df_):
    if df_.empty:
        return None
    return px.box(df_, x="qualite_isolation_murs", y="conso_m2",
                  title="Consommation vs qualité isolation des murs",
                  labels={"qualite_isolation_murs":"Qualité isolation murs", "conso_m2":"kWh/m²/an"})

def fig_conso_par_annee(df_):
    if df_.empty:
        return None

    ordre = ["avant_1948", "1949_1974", "1975_1989", "1990_1999", "2000_2011", "apres_2012"]
    tmp = df_.groupby("classe_annee_construction", as_index=False)["conso_m2"].mean()
    tmp["classe_annee_construction"] = pd.Categorical(tmp["classe_annee_construction"], categories=ordre, ordered=True)
    tmp = tmp.sort_values("classe_annee_construction")

    # Graphique Plotly
    fig = px.bar(
        tmp,
        x="classe_annee_construction",
        y="conso_m2",
        title="Conso moyenne par classe d’année de construction",
        labels={"conso_m2": "kWh/m²/an", "classe_annee_construction": "Classe année"},
        category_orders={"classe_annee_construction": ordre},  # 👈 renforce l'ordre dans Plotly
        color="classe_annee_construction",
        color_discrete_sequence=px.colors.sequential.Viridis
    )

    fig.update_layout(
        xaxis_title="Classe d'année de construction",
        yaxis_title="Consommation moyenne (kWh/m²/an)",
        margin=dict(l=0, r=0, t=40, b=0)
    )

    return fig

def fig_carte_choropleth(df_):
    """
    Carte choroplèthe par commune.
    - Si un GeoJSON est disponible dans data/communes69.geojson (id: NOM or NOM_COM), on l’utilise.
    - Sinon, fallback: carte à bulles sur centroïdes communaux colorées par conso moyenne.
    """
    if df_.empty:
        return None

    # Agrégation par commune
    agg = df_.groupby("nom_commune_ban", as_index=False).agg(
        conso_m2_mean=("conso_m2","mean"),
        lon=("lon","mean"),
        lat=("lat","mean"),
        n=("row_id","count")
    ).dropna(subset=["lat","lon"])


    # Tenter GeoJSON
    gj_path = Path(__file__).parent.parent / "data" / "communes69.geojson"
    if gj_path.exists():
        import json
        with open(gj_path, "r", encoding="utf-8") as f:
            geojson = json.load(f)

        # On suppose que la clé d'identité s'appelle "NOM" ou "nom_commune_ban"
        # Harmoniser les noms (upper) pour le matching
        agg["key"] = agg["nom_commune_ban"].str.upper().str.normalize("NFKD").str.encode("ascii","ignore").str.decode("ascii")
        # Heuristique de clé geojson
        feature_keys = ["properties.NOM", "properties.NOM_COM", "properties.nom", "properties.NOM_COMM"]
        featureidkey = None
        # Essayer de détecter la clé
        sample_props = geojson["features"][0]["properties"]
        for k in ["NOM","NOM_COM","nom","NOM_COMM"]:
            if k in sample_props:
                featureidkey = f"properties.{k}"
                break
        if featureidkey is None:
            featureidkey = "properties.NOM"

        # Construire une série 'locations' en alignant les noms si possible
        # Pour éviter les mismatches, on copie 'locations' = agg['key'] et on modifie le geojson en upper
        # (Risque: nécessite normalisation côté geojson. Si mismatch, fallback bulle.)
        try:
            fig = px.choropleth_mapbox(
                agg,
                geojson=geojson,
                locations="nom_commune_ban",  # on tente nom_commune tel quel
                color="conso_m2_mean",
                featureidkey=featureidkey,
                hover_name="nom_commune_ban",
                hover_data={"conso_m2_mean":":.1f", "n":True},
                color_continuous_scale="YlOrRd",
                mapbox_style="open-street-map",
                center={"lat": float(agg["lat"].mean()), "lon": float(agg["lon"].mean())},
                zoom=8,
                opacity=0.7,
                height=650,
                title="Carte choroplèthe – Conso moyenne (kWh/m²/an) par commune"
            )
            fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
            return fig
        except Exception:
            pass  # si ça échoue, fallback

    # Fallback: carte points (centroïdes) colorés par conso moyenne
    fig = px.scatter_map(
        agg,
        lat="lat", lon="lon",
        size="n",
        color="conso_m2_mean",
        color_continuous_scale="YlOrRd",
        hover_name="nom_commune_ban",
        hover_data={"conso_m2_mean":":.1f","n":True,"lat":False,"lon":False},
        title="Carte (fallback) – Centroïdes par commune, taille = nb logements, couleur = conso moyenne",
        height=650,
        zoom=10
    )
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_center={"lat": float(agg["lat"].mean()), "lon": float(agg["lon"].mean())},
        margin=dict(l=0, r=0, t=40, b=0)
    )
    fig.update_traces(marker=dict(opacity=0.85))
    return fig



def fig_ges_par_dpe(df_):
    """Affiche la moyenne des émissions GES par étiquette DPE."""
    if df_.empty:
        return None

    # Calcul de la moyenne et de l'écart-type pour info
    tmp = df_.groupby("etiquette_dpe", as_index=False).agg(
        ges_moy=("emission_ges_5_usages", "mean"),
        ges_std=("emission_ges_5_usages", "std"),
        n=("emission_ges_5_usages", "count")
    ).sort_values("etiquette_dpe")

    fig = px.bar(
        tmp,
        x="etiquette_dpe",
        y="ges_moy",
        color="etiquette_dpe",
        color_discrete_map=dpe_color_map,
        title="Émissions GES moyennes par étiquette DPE (kgCO₂e/an)",
        text=tmp["ges_moy"].round(1).astype(str) + " kgCO₂e"
    )

    # Ajout d’erreurs visuelles pour montrer la dispersion
    fig.update_traces(
        textposition="outside",
        error_y=dict(array=tmp["ges_std"], color="gray", thickness=1, width=5)
    )

    fig.update_layout(
        xaxis_title="Étiquette DPE",
        yaxis_title="Émissions moyennes de GES (kgCO₂e/an)",
        margin=dict(l=0, r=0, t=60, b=0)
    )

    return fig


def fig_dpe_par_energie(df_):
    if df_.empty:
        return None
    tmp = df_.groupby(["type_energie_principale_chauffage", "etiquette_dpe"], as_index=False).size()
    tmp.rename(columns={"size": "count"}, inplace=True)
    fig = px.bar(
        tmp,
        x="type_energie_principale_chauffage",
        y="count",
        color="etiquette_dpe",
        color_discrete_map=dpe_color_map,
        title="Répartition DPE par type d’énergie principale",
        barmode="stack"
    )
    fig.update_layout(xaxis_title="Type d’énergie", yaxis_title="Nombre de logements")
    return fig



def compute_center_zoom(df: pd.DataFrame):
    """Calcule le centre et le zoom pour une carte selon l’emprise lat/lon."""
    if df.empty or {"lat", "lon"}.difference(df.columns):
        return {"lat": 45.75, "lon": 4.85}, 8  # Lyon par défaut

    lat_min, lat_max = df["lat"].min(), df["lat"].max()
    lon_min, lon_max = df["lon"].min(), df["lon"].max()
    center = {"lat": float((lat_min + lat_max) / 2), "lon": float((lon_min + lon_max) / 2)}
    span = max(lat_max - lat_min, lon_max - lon_min)

    if span < 0.01: zoom = 14
    elif span < 0.02: zoom = 13
    elif span < 0.05: zoom = 12
    elif span < 0.10: zoom = 11
    elif span < 0.20: zoom = 10
    elif span < 0.50: zoom = 9
    elif span < 1.00: zoom = 8
    else: zoom = 7

    zoom *= 1.05
    return center, zoom


def fig_carte_points(df_):
    """Carte interactive : points de logements colorés par étiquette DPE."""
    if df_.empty:
        return None

    df_geo = df_.dropna(subset=["lat", "lon"]).copy()
    color_map = dict(df_geo.groupby("etiquette_dpe")["color_dpe"].first()) or {
        "A": "#00FF00", "B": "#7FFF00", "C": "#FFFF00",
        "D": "#FFD700", "E": "#FFA500", "F": "#FF4500", "G": "#FF0000"
    }

    center, zoom = compute_center_zoom(df_geo)
    sample_n = min(5000, len(df_geo))
    plot_df = df_geo.sample(sample_n, random_state=42) if len(df_geo) > sample_n else df_geo

    fig = px.scatter_mapbox(
        plot_df,
        lat="lat",
        lon="lon",
        color="etiquette_dpe",
        color_discrete_map=color_map,
        hover_name="nom_commune_ban",
        hover_data=[
            "type_batiment", "surface_habitable_logement", "etiquette_dpe", "conso_m2", "cout_m2"
        ],
        height=650,
        title="Répartition géographique des logements par classe DPE (Rhône 69)",
        zoom=zoom
    )

    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_center=center,
        margin=dict(l=0, r=0, t=40, b=0),
        hoverlabel=dict(bgcolor="white", font_size=12),
        dragmode="zoom"
    )
    fig.update_traces(marker=dict(opacity=0.85, size=6))  # 🔹 taille fixe

    return fig


# ========= SÉLECTION DE VISU =========
st.markdown("### Visualisations")

VISU_CHOICES = {
    "Répartition par étiquette DPE": fig_repartition_dpe,
    "Conso moyenne par type de bâtiment": fig_conso_par_type_bat,
    "Top 25 coût moyen par commune": fig_cout_par_commune,
    "Distribution de la conso (histogramme)": fig_hist_conso,
    "Coût par étiquette (boxplot)": fig_box_cout_par_dpe,
    "Répartition DPE par zone climatique": fig_dpe_par_zone,
    "Répartition énergies (camembert)": fig_energie_pie,
    "Conso vs isolation murs (boxplot)": fig_isolation_vs_conso,
    "Conso par classe d’année": fig_conso_par_annee,
    "Carte choroplèthe par commune": fig_carte_choropleth,
    "Moyenne des GES par étiquette DPE": fig_ges_par_dpe,
    "Répartition DPE par type d’énergie": fig_dpe_par_energie,
    "Carte points des logements (DPE)": fig_carte_points,
}

default_selection = [
    "Répartition par étiquette DPE",
    "Coût par étiquette (boxplot)",
    "Top 25 coût moyen par commune",
    "Conso vs isolation murs (boxplot)",
]

selected = st.multiselect(
    "Choisissez jusqu’à 4 visualisations à afficher",
    options=list(VISU_CHOICES.keys()),
    default=default_selection,
    max_selections=4
)

# Affichage en grille
cols_layout = st.columns(2)
slot = 0
for name in selected:
    fig_builder = VISU_CHOICES[name]
    fig = fig_builder(filtered)
    if fig is None:
        with cols_layout[slot % 2]:
            st.warning(f"Pas de données suffisantes pour « {name} ».")
    else:
        with cols_layout[slot % 2]:
            #st.plotly_chart(fig, width="stretch", config={"displaylogo": False})
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0.03)",
                plot_bgcolor="rgba(255,255,255,0)",
                margin=dict(l=10, r=10, t=50, b=10)
            )
            st.plotly_chart(
                fig,
                config={
                    "displaylogo": False,
                    "responsive": True,
                    "scrollZoom": True,
                    "showTips": False,
                    "modeBarButtonsToRemove": ["select2d", "lasso2d"]
                }
            )
            


    slot += 1


# ========= TABLEAU & EXPORT =========
st.markdown("### Données filtrées")
with st.expander("Voir / exporter les données filtrées"):
    st.caption("Aperçu des données utilisées par le dashboard.")
    st.dataframe(
        filtered[
            [
                "row_id", "nom_commune_ban", "type_batiment", "surface_habitable_logement",
                "etiquette_dpe", "conso_m2", "cout_m2", "emission_ges_5_usages",
                "type_energie_principale_chauffage", "classe_annee_construction",
                "zone_climatique", "lat", "lon", "color_dpe"
            ]
        ].reset_index(drop=True),
        width="stretch",
        height=420
    )

    st.markdown("---")
    st.markdown("#### Export des données et visualisations")

    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "Télécharger les données filtrées (CSV)",
            data=filtered.to_csv(index=False).encode("utf-8"),
            file_name="dpe_filtre.csv",
            mime="text/csv",
            use_container_width=True
        )

    with c2:
        if not selected:
            st.info("Sélectionnez d’abord des visualisations pour activer l’export HTML.")
        else:
            export_choice = st.selectbox(
                "Choisir la visualisation à exporter (applique les filtres actifs)",
                options=selected,
                index=0,
                help="Sélectionnez la visualisation à enregistrer en HTML interactif. "
                     "Les filtres appliqués dans le dashboard seront conservés."
            )

            if st.button("Exporter cette visualisation en HTML interactif"):
                with st.spinner("Génération du fichier HTML interactif..."):
                    fig_to_export = VISU_CHOICES[export_choice](filtered)
                    if fig_to_export is not None:
                        html_bytes = fig_to_export.to_html(include_plotlyjs="cdn").encode("utf-8")
                        st.download_button(
                            "Télécharger le fichier HTML",
                            data=html_bytes,
                            file_name=f"visualisation_{export_choice.replace(' ', '_')}.html",
                            mime="text/html",
                            use_container_width=True
                        )
                    else:
                        st.warning("Impossible d’exporter : cette visualisation ne contient pas de données.")

