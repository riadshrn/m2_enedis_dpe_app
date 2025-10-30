import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from pathlib import Path
from typing import Optional, Union
from utils.layout import render_sidebar, load_css

# Charger les styles et la sidebar commune
load_css()
render_sidebar()

# === CONFIG ===
logo_path = Path(__file__).parent.parent / "assets" / "logo-removebg.png"
# ========= CONFIG & STYLES =========
st.set_page_config(
    page_title="Visualisation dynamique DPE",
    page_icon=logo_path,
    layout="wide"
)
# API_BASE = "http://localhost:8000"
API_BASE = "https://riadshrn-api-dpe-conso.hf.space"

# === HEADER ===
st.markdown("""
<div class="main-header fade-in">
    <h1>Visualisation dynamique des données DPE</h1>
    <p>Créez des graphiques interactifs à partir des colonnes sélectionnées</p>
</div>
""", unsafe_allow_html=True)

# === Utilitaires DPE ===
ORDRE_DPE = ["A", "B", "C", "D", "E", "F", "G"]

def build_color_map(df: pd.DataFrame) -> dict:
    """Construit un mapping etiquette_dpe -> couleur HEX."""
    fallback = {
        "A": "#009966",
        "B": "#66CC00",
        "C": "#CCFF00",
        "D": "#FFCC00",
        "E": "#FF9900",
        "F": "#FF6600",
        "G": "#CC0000",
    }
    if {"etiquette_dpe", "color_dpe"}.issubset(df.columns):
        m = (
            df[["etiquette_dpe", "color_dpe"]]
            .dropna()
            .drop_duplicates()
            .set_index("etiquette_dpe")["color_dpe"]
            .to_dict()
        )
        return {k: m.get(k, fallback[k]) for k in ORDRE_DPE}
    return fallback

def add_category_orders(kwargs: dict, df: pd.DataFrame, col_names: list):
    """Ajoute category_orders pour forcer A→G sur les colonnes passées."""
    if "category_orders" not in kwargs:
        kwargs["category_orders"] = {}
    for c in col_names:
        if c in df.columns:
            kwargs["category_orders"][c] = ORDRE_DPE

# ---------------------------------------------------------
# Fonction : générer un graphique Plotly
# ---------------------------------------------------------
def generer_graphique_plotly(
    df: pd.DataFrame,
    type_graphique: str,
    x: str,
    y: Optional[str] = None,
    z: Optional[str] = None,
    titre: Optional[str] = None,
    **kwargs
) -> Union[go.Figure, None]:
    """Génère un graphique Plotly selon le type spécifié."""
    types_valides = {
        'scatter', 'line', 'bar', 'histogram', 'box',
        'violin', 'pie', 'scatter_3d', 'density_heatmap', 'area'
    }

    if type_graphique not in types_valides:
        st.error(f"Type '{type_graphique}' non supporté.")
        return None

    if df.empty:
        st.warning("Le DataFrame est vide.")
        return None

    titre = titre or f"{type_graphique.capitalize()} : {y or x}"

    try:
        if type_graphique == "scatter":
            fig = px.scatter(df, x=x, y=y, title=titre, **kwargs)
        elif type_graphique == "line":
            fig = px.line(df, x=x, y=y, title=titre, **kwargs)
        elif type_graphique == "bar":
            fig = px.bar(df, x=x, y=y, title=titre, **kwargs)
        elif type_graphique == "histogram":
            fig = px.histogram(df, x=x, title=titre, **kwargs)
        elif type_graphique == "box":
            fig = px.box(df, x=x, y=y, title=titre, **kwargs)
        elif type_graphique == "violin":
            fig = px.violin(df, x=x, y=y, title=titre, **kwargs)
        elif type_graphique == "pie":
            fig = px.pie(df, title=titre, **kwargs)
        elif type_graphique == "scatter_3d":
            fig = px.scatter_3d(df, x=x, y=y, z=z, title=titre, **kwargs)
        elif type_graphique == "density_heatmap":
            fig = px.density_heatmap(df, x=x, y=y, title=titre, **kwargs)
        elif type_graphique == "area":
            fig = px.area(df, x=x, y=y, title=titre, **kwargs)

        # === Forcer l'ordre des axes et légendes ===
        if "etiquette_dpe" in df.columns:
            fig.update_xaxes(categoryorder="array", categoryarray=ORDRE_DPE)
            fig.update_yaxes(categoryorder="array", categoryarray=ORDRE_DPE)
            fig.update_layout(legend=dict(traceorder="normal"))

        fig.update_layout(template="plotly_white",
                          title_font=dict(size=18),
                          font=dict(size=12))
        return fig

    except Exception as e:
        st.error(f"Erreur génération graphique : {e}")
        return None

# ---------------------------------------------------------
# Récupération et chargement des données
# ---------------------------------------------------------
@st.cache_data(ttl=1800)
def get_colonnes_disponibles():
    try:
        r = requests.get(f"{API_BASE}/data/detail/1", timeout=15)
        r.raise_for_status()
        logement = r.json().get("logement", {})
        return list(logement.keys())
    except Exception as e:
        st.error(f"Erreur récupération colonnes : {e}")
        return []

@st.cache_data(ttl=1800)
def charger_donnees(cols: list):
    try:
        r = requests.get(
            f"{API_BASE}/data/select",
            params={"columns": cols, "size": 100000},
            timeout=30
        )
        r.raise_for_status()
        data = r.json().get("data", [])
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Erreur chargement données : {e}")
        return pd.DataFrame()

# ---------------------------------------------------------
# Interface principale
# ---------------------------------------------------------
st.markdown("### Sélection et chargement des données")
colonnes = get_colonnes_disponibles()
if not colonnes:
    st.stop()

colonnes_sel = st.multiselect(
    "Choisissez les colonnes à charger depuis l'API :",
    colonnes,
    default=["surface_habitable_logement", "etiquette_dpe", "conso_m2"]
)

if st.button("Charger les données sélectionnées", use_container_width=True):
    st.session_state.df_viz = charger_donnees(colonnes_sel)

df = st.session_state.get("df_viz", pd.DataFrame())
if df.empty:
    st.info("Sélectionnez des colonnes et cliquez sur *Charger les données* pour continuer.")
    st.stop()
else:
    st.success(f"Données chargées ({len(df):,} lignes, {len(df.columns)} colonnes).")

if "etiquette_dpe" in df.columns:
    df["etiquette_dpe"] = pd.Categorical(df["etiquette_dpe"], categories=ORDRE_DPE, ordered=True)

# ---------------------------------------------------------
# Visualisation du DataFrame
# ---------------------------------------------------------
with st.expander("Voir les données utilisées pour la visualisation"):
    st.dataframe(
        df,
        use_container_width=True,
        height=420,
        key="filtered_df"
    )

# ---------------------------------------------------------
# Configuration du graphique
# ---------------------------------------------------------
st.markdown("### Configuration du graphique")

c1, c2, c3 = st.columns(3)
with c1:
    type_graph = st.selectbox("Type de graphique", [
        "scatter", "histogram", "box",
        "violin", "pie", "scatter_3d", "density_heatmap", "area"
    ])
with c2:
    x_col = st.selectbox("Axe X", df.columns)
with c3:
    y_col = st.selectbox("Axe Y (optionnel)", [""] + list(df.columns))

c4, c5 = st.columns(2)
with c4:
    color_col = st.selectbox("Couleur (optionnelle)", [""] + list(df.columns))
with c5:
    z_col = st.selectbox("Z / Facet (optionnel pour 3D)", [""] + list(df.columns))

titre = st.text_input("Titre du graphique", value=f"{type_graph.capitalize()} - {x_col}")

# ---------------------------------------------------------
# Génération du graphique
# ---------------------------------------------------------
st.markdown("### Résultat du graphique")

if st.button("Générer le graphique", type="primary", use_container_width=True):
    kwargs = {}
    color_map = build_color_map(df)
    add_category_orders(kwargs, df, ["etiquette_dpe", x_col, y_col])

    # === Gestion automatique de la couleur ===
    if color_col == "color_dpe" or color_col == "etiquette_dpe":
        kwargs["color"] = "etiquette_dpe"
        kwargs["color_discrete_map"] = color_map
    elif color_col:
        kwargs["color"] = color_col

    # Cas particuliers pour area / box / violin qui nécessitent un color explicite
    if type_graph in ["box", "violin", "area"] and "etiquette_dpe" in df.columns and "color" not in kwargs:
        kwargs["color"] = "etiquette_dpe"
        kwargs["color_discrete_map"] = color_map

    # Cas particulier histogramme
    if type_graph == "histogram" and "color" not in kwargs and "etiquette_dpe" in df.columns:
        kwargs["color"] = "etiquette_dpe"
        kwargs["color_discrete_map"] = color_map

    # Cas particulier pie
    if type_graph == "pie":
        kwargs["names"] = x_col if x_col in df.columns else "etiquette_dpe"
        kwargs["values"] = y_col or None
        if "color" not in kwargs:
            kwargs["color"] = "etiquette_dpe"
            kwargs["color_discrete_map"] = color_map
        add_category_orders(kwargs, df, [kwargs["names"], "etiquette_dpe"])

    # Génération du graphique
    fig = generer_graphique_plotly(
        df,
        type_graphique=type_graph,
        x=x_col,
        y=y_col or None,
        z=z_col or None,
        titre=titre,
        **kwargs
    )

    if fig:
        st.plotly_chart(fig, use_container_width=True)
                # ---------- EXPORTS ----------
        st.markdown("---")
        st.subheader("Exporter les résultats")

        from io import BytesIO
        import base64

        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                "Télécharger les données (CSV)",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="donnees_visualisation.csv",
                mime="text/csv",
                use_container_width=True
            )

        with c2:
            buf = BytesIO()
            try:
                # Sauvegarde du graphique en image (nécessite kaleido)
                fig.write_image(buf, format="png", scale=2)
                st.download_button(
                    "Télécharger le graphique (PNG)",
                    data=buf.getvalue(),
                    file_name="graphique_dpe.png",
                    mime="image/png",
                    use_container_width=True
                )
            except Exception:
                st.warning("Export PNG indisponible (bibliothèque 'kaleido' manquante). Installez-la avec `pip install kaleido`.")

    else:
        st.error("Erreur lors de la génération du graphique.")

else:
    st.info("Configurez vos paramètres et cliquez sur *Générer le graphique*.")
