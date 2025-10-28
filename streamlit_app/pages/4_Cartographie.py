import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from pathlib import Path
from io import BytesIO

# === CONFIG ===
st.set_page_config(page_title="Cartographie DPE Rhône 69", page_icon="🗺️", layout="wide")
API_BASE = "http://localhost:8000"
# API_BASE = "https://riadshrn-api-dpe-conso.hf.space"

# === CSS ===
def load_css():
    css_file = Path(__file__).parent.parent / "assets" / "styles.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css()

st.markdown("""
<div class="main-header fade-in">
  <h1>🗺️ Cartographie des logements – Rhône (69)</h1>
  <p>Explorez, filtrez et exportez les données DPE locales</p>
</div>
""", unsafe_allow_html=True)

# ---------- UTILS ----------
def compute_center_zoom(df: pd.DataFrame):
    """Calcule un centre + zoom dynamique selon l’emprise lat/lon."""
    if df.empty or {"lat", "lon"}.difference(df.columns):
        return {"lat": 45.75, "lon": 4.85}, 8  # Lyon par défaut

    lat_min, lat_max = df["lat"].min(), df["lat"].max()
    lon_min, lon_max = df["lon"].min(), df["lon"].max()
    center = {"lat": float((lat_min + lat_max)/2), "lon": float((lon_min + lon_max)/2)}
    span = max(lat_max - lat_min, lon_max - lon_min)

    if span < 0.01: zoom = 14
    elif span < 0.02: zoom = 13
    elif span < 0.05: zoom = 12
    elif span < 0.10: zoom = 11
    elif span < 0.20: zoom = 10
    elif span < 0.50: zoom = 9
    elif span < 1.00: zoom = 8
    else: zoom = 7
    return center, zoom

# ---------- DATA ----------
@st.cache_data(ttl=1800)
def load_data():
    cols = [
        "nom_commune_ban", "type_batiment", "surface_habitable_logement",
        "etiquette_dpe", "lon", "lat", "conso_m2", "cout_m2", "color_dpe"
    ]
    r = requests.get(f"{API_BASE}/data/select", params={"columns": cols, "size": 50000}, timeout=30)
    r.raise_for_status()
    df = pd.DataFrame(r.json().get("data", []))
    if "row_id" not in df.columns:
        df = df.reset_index(names="row_id")
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Erreur API: {e}")
    st.stop()

if df.empty:
    st.warning("Aucune donnée chargée.")
    st.stop()

# ---------- FILTRES ----------
st.markdown("## 🎛️ Filtres")

c1, c2, c3, c4 = st.columns(4)
with c1:
    commune_sel = st.multiselect("🏙️ Commune", sorted(df["nom_commune_ban"].dropna().unique()))
with c2:
    type_bat_sel = st.multiselect("🏠 Type de bâtiment", sorted(df["type_batiment"].dropna().unique()))
with c3:
    etiquettes_sel = st.multiselect("📊 Étiquette DPE", sorted(df["etiquette_dpe"].dropna().unique()))
with c4:
    surface_range = st.slider("Surface habitable (m²)", 10, int(df["surface_habitable_logement"].max()), (20, 200))

c5, c6 = st.columns(2)
with c5:
    conso_range = st.slider("Consommation (kWh/m²/an)", 0, int(df["conso_m2"].max()), (0, 300))
with c6:
    cout_range = st.slider("Coût (€/m²/an)", 0, int(df["cout_m2"].max()), (0, int(df["cout_m2"].max()/2)))

filtered = df.copy()
if commune_sel:
    filtered = filtered[filtered["nom_commune_ban"].isin(commune_sel)]
if type_bat_sel:
    filtered = filtered[filtered["type_batiment"].isin(type_bat_sel)]
if etiquettes_sel:
    filtered = filtered[filtered["etiquette_dpe"].isin(etiquettes_sel)]
filtered = filtered[
    filtered["surface_habitable_logement"].between(*surface_range)
    & filtered["conso_m2"].between(*conso_range)
    & filtered["cout_m2"].between(*cout_range)
]

st.success(f"{len(filtered):,} logements affichés (sur {len(df):,})")

# ---------- CARTE ----------
st.markdown('<div id="cartographie-des-logements-rhone-69"></div>', unsafe_allow_html=True)
st.markdown("### 🌍 Carte interactive")

df_geo = filtered.dropna(subset=["lat", "lon"]).copy()
color_map = dict(df_geo.groupby("etiquette_dpe")["color_dpe"].first()) or {
    "A": "#00FF00", "B": "#7FFF00", "C": "#FFFF00",
    "D": "#FFD700", "E": "#FFA500", "F": "#FF4500", "G": "#FF0000"
}

center, zoom = compute_center_zoom(df_geo if not df_geo.empty else filtered)
sample_n = min(5000, len(df_geo))
plot_df = df_geo.sample(sample_n, random_state=42) if len(df_geo) > sample_n else df_geo

fig = px.scatter_mapbox(
    plot_df,
    lat="lat", lon="lon",
    color="etiquette_dpe",
    size="surface_habitable_logement",
    color_discrete_map=color_map,
    hover_name="nom_commune_ban",
    hover_data={
        "row_id": True, "type_batiment": True,
        "surface_habitable_logement": True, "conso_m2": True, "cout_m2": True
    },
    height=700,
    title="Répartition géographique des logements par classe DPE (Rhône 69)",
    zoom=zoom
)
fig.update_layout(
    mapbox_style="carto-positron",
    mapbox_center=center,
    margin=dict(l=0, r=0, t=40, b=0),
    hoverlabel=dict(bgcolor="white", font_size=12),
    dragmode="zoom"
)
fig.update_traces(marker=dict(opacity=0.85))

st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True, "displaylogo": False})

# ---------- TABLEAU INTERACTIF ----------
with st.expander("👁️ Voir les données utilisées pour la carte"):
    st.caption("💡 Cliquez une ligne pour ouvrir la fiche. Une seule sélection à la fois est autorisée.")
    st.dataframe(
        filtered,
        use_container_width=True,
        height=420,
        on_select="rerun",
        key="filtered_df",
        selection_mode="single-row",   # <- force 1 seule ligne
    )

# ---------- FICHE TECHNIQUE LOGEMENT ----------
if "show_card" not in st.session_state:
    st.session_state.show_card = False
if "selected_row_id" not in st.session_state:
    st.session_state.selected_row_id = None

# Récupérer la sélection depuis le session_state (pas via le retour de st.dataframe)
sel_state = st.session_state.get("filtered_df", {})
rows = sel_state.get("selection", {}).get("rows", [])

if rows:
    try:
        idx = rows[0]                          # première (et seule) ligne
        new_row_id = int(filtered.iloc[idx]["row_id"])

        if st.session_state.selected_row_id != new_row_id:
            st.session_state.selected_row_id = new_row_id
            st.session_state.show_card = True

        # 🔄 Réinitialiser la sélection pour éviter les multiples lignes/états fantômes
        try:
            st.session_state["filtered_df"]["selection"]["rows"].clear()
        except Exception:
            st.session_state["filtered_df"]["selection"]["rows"] = []

        st.rerun()
    except Exception as e:
        st.error(f"Erreur sélection: {e}")

# Affichage de la fiche sous la carte
if st.session_state.show_card and st.session_state.selected_row_id is not None:
    st.markdown("---")
    st.markdown("### 🏠 Fiche technique du logement sélectionné")

    try:
        r = requests.get(f"{API_BASE}/data/detail/{st.session_state.selected_row_id}", timeout=15)
        r.raise_for_status()
        lg = r.json().get("logement", {})
        if lg:
            color = lg.get("color_dpe", "#888")
            st.markdown(
                f"""
                <div style="border: 3px solid {color}; border-radius: 14px; padding: 14px; background-color:#fafafa;">
                    <h3 style="margin-top:0;">{lg.get('type_batiment','Logement')}</h3>
                    <p><b>Commune :</b> {lg.get('nom_commune_ban')} ({lg.get('code_postal_ban','N/A')})</p>
                    <p><b>Étiquette DPE :</b> <span style="color:{color};font-weight:bold;">{lg.get('etiquette_dpe')}</span></p>
                    <p><b>Surface :</b> {lg.get('surface_habitable_logement')} m²</p>
                    <p><b>Conso :</b> {lg.get('conso_m2')} kWh/m²/an</p>
                    <p><b>Coût :</b> {lg.get('cout_m2')} €/m²/an</p>
                    <p><b>Énergie principale :</b> {lg.get('type_energie_principale_chauffage','N/A')}</p>
                    <p><b>Ancienneté :</b> {lg.get('anciennete','N/A')} ans</p>
                    <p><b>Classe construction :</b> {lg.get('classe_annee_construction','N/A')}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.warning("Aucun logement trouvé.")
    except Exception as e:
        st.error(f"Erreur: {e}")

# ---------- EXPORTS ----------
st.markdown("---")

c1, c2 = st.columns(2)
with c1:
    st.download_button(
        "📁 Télécharger les données filtrées (CSV)",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="donnees_filtrees_cartographie.csv",
        mime="text/csv",
        use_container_width=True
    )

with c2:
    buf = BytesIO()
    fig.write_image(buf, format="png", scale=2)
    st.download_button(
        "🖼️ Enregistrer la carte (PNG)",
        data=buf.getvalue(),
        file_name="carte_dpe_rhone.png",
        mime="image/png",
        use_container_width=True
    )
