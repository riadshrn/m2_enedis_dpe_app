import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import numpy as np
from io import BytesIO
from pathlib import Path
from datetime import datetime
from utils.layout import render_sidebar, load_css
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from pathlib import Path
import tempfile
import zipfile
import io



# ========== CONFIG ==========
logo_path = Path(__file__).parent.parent / "assets" / "logo-removebg.png"
st.set_page_config(page_title="DPE ADEME par commune", page_icon=logo_path, layout="wide")

load_css()
render_sidebar()

# ========== HEADER ==========
st.markdown("""
<div class="main-header fade-in">
  <h1>DPE x ADEME InRealTime</h1>
  <p>Consultez ou comparez les DPE neufs par commune</p>
</div>
""", unsafe_allow_html=True)

# ========== CHARGEMENT DES COMMUNES ==========
csv_communes_path = Path(__file__).parent.parent / "data" / "communes_ademe_par_dep.csv"

try:
    communes_df = pd.read_csv(csv_communes_path)
    communes_df = communes_df.dropna().sort_values("nom_commune_ban").reset_index(drop=True)
except Exception as e:
    st.error(f"Impossible de charger la liste des communes : {e}")
    st.stop()

# ====================================================
# ⚙️ Fonctions utilitaires
# ====================================================
def fetch_dpe_by_commune(nom_commune: str, limit: int = 10000, pages: int = 10):
    base_url = "https://data.ademe.fr/data-fair/api/v1/datasets/dpe02neuf/lines"
    all_results = []
    for page in range(1, pages + 1):
        params = {
            "qs": f'nom_commune_ban:"{nom_commune}"',
            "size": min(limit, 1000),
            "page": page,
            "select": "nom_commune_ban,type_batiment,surface_habitable_logement,etiquette_dpe,_geopoint,conso_5_usages_par_m2_ep,cout_total_5_usages,code_postal_ban,date_reception_dpe",
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
    df = pd.json_normalize(all_results)

    if "_score" in df.columns:
        df = df.drop(columns=["_score"])

    return df

def preprocess_dpe_api(df_api: pd.DataFrame) -> pd.DataFrame:
    if df_api.empty:
        return df_api
    if "_geopoint" in df_api.columns:
        coords = df_api["_geopoint"].str.split(",", expand=True)
        df_api["lat"] = coords[0].astype(float)
        df_api["lon"] = coords[1].astype(float)
    if "date_reception_dpe" in df_api.columns:
        df_api["date_reception_dpe"] = pd.to_datetime(df_api["date_reception_dpe"], errors="coerce")
    df_api["conso_m2"] = df_api["conso_5_usages_par_m2_ep"]
    df_api["cout_m2"] = df_api["cout_total_5_usages"] / df_api["surface_habitable_logement"]
    color_map = {"A": "#00FF00", "B": "#7FFF00", "C": "#FFFF00",
                 "D": "#FFD700", "E": "#FFA500", "F": "#FF4500", "G": "#FF0000"}
    df_api["color_dpe"] = df_api["etiquette_dpe"].map(color_map).fillna("#999999")
    df_api["source"] = "ADEME"
    return df_api

def compute_center_zoom(df):
    if df.empty or {"lat", "lon"}.difference(df.columns):
        return {"lat": 46.6, "lon": 2.5}, 6
    lat_min, lat_max = df["lat"].min(), df["lat"].max()
    lon_min, lon_max = df["lon"].min(), df["lon"].max()
    center = {"lat": (lat_min + lat_max) / 2, "lon": (lon_min + lon_max) / 2}
    span = max(lat_max - lat_min, lon_max - lon_min)
    zoom = 13 if span < 0.02 else 10 if span < 0.5 else 8
    return center, zoom

def generate_pdf_report(communes_data, date_range):
    """Génère un rapport PDF ADEME comparatif (format paysage) avec tableau, cartes côte à côte et données."""
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    # Format paysage
    doc = SimpleDocTemplate(tmp_file.name, pagesize=landscape(A4),
                            leftMargin=1.5 * cm, rightMargin=1.5 * cm,
                            topMargin=1 * cm, bottomMargin=1 * cm)
    story = []

    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        "TitleCentered",
        parent=styles["Title"],
        alignment=1,
        spaceAfter=12,
    )
    style_sub = ParagraphStyle(
        "SubHeading",
        parent=styles["Heading2"],
        spaceBefore=10,
        spaceAfter=6,
    )
    style_normal = ParagraphStyle(
        "NormalJustify",
        parent=styles["Normal"],
        leading=15,
        spaceAfter=6,
    )

    # === PAGE D'EN-TÊTE ===
    logo_path = Path(__file__).parent.parent / "assets" / "logo-removebg.png"
    try:
        story.append(Image(str(logo_path), width=4 * cm, height=4 * cm))
    except Exception:
        story.append(Paragraph("<b>GREENTECH SOLUTIONS</b>", style_normal))

    story.append(Paragraph("<b>Rapport comparatif DPE ADEME</b>", style_title))
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        f"Période analysée : <b>{date_range[0].date()} → {date_range[1].date()}</b>",
        style_normal
    ))
    story.append(Spacer(1, 24))

    # === TABLEAU COMPARATIF DES STATISTIQUES ===
    table_data = [["Commune", "Nouveaux logements", "DPE dominant",
                   "Conso. moyenne (kWh/m²/an)", "Coût moyen (€/m²/an)"]]
    for data in communes_data:
        c = data["commune"]
        s = data["stats"]
        table_data.append([
            c,
            f"{s['nb']:,}",
            s["dpe"],
            f"{s['conso']:.1f}",
            f"{s['cout']:.1f}"
        ])

    table = Table(table_data, colWidths=[5*cm, 4*cm, 4*cm, 5*cm, 5*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
    ]))
    story.append(table)
    story.append(Spacer(1, 20))

    # === CARTES CÔTE À CÔTE (COMMUNE 1 & 2) ===
    story.append(Paragraph("<b>Cartes des communes comparées</b>", style_sub))
    story.append(Spacer(1, 8))

    row_images = []
    for data in communes_data:
        try:
            img = Image(data["img_path"], width=12 * cm, height=8 * cm)
            row_images.append(img)
        except Exception:
            row_images.append(Paragraph("Carte non disponible", style_normal))

    story.append(Table([row_images], colWidths=[14 * cm, 14 * cm]))
    story.append(PageBreak())

    # === DÉTAIL DES DONNÉES POUR CHAQUE COMMUNE ===
    for data in communes_data:
        commune = data["commune"]
        df = data.get("df")
        story.append(Paragraph(f"<b>Données brutes – {commune}</b>", style_sub))
        story.append(Spacer(1, 6))

        if isinstance(df, pd.DataFrame) and not df.empty:
            colonnes_utiles = [
                "date_reception_dpe",
                "code_postal_ban",
                "surface_habitable_logement",
                "etiquette_dpe",
                "conso_m2",
                "cout_m2",
            ]
            df = df[[c for c in colonnes_utiles if c in df.columns]].copy()

            preview = df.head(25).round(2)
            table_data = [list(preview.columns)] + preview.astype(str).values.tolist()
            table = Table(table_data, repeatRows=1, colWidths=[4*cm] * len(preview.columns))
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.grey),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke)
            ]))
            story.append(table)
        else:
            story.append(Paragraph("Aucune donnée disponible.", style_normal))

        story.append(PageBreak())

    doc.build(story)
    return tmp_file.name


# === CHOIX DU MODE ===
st.markdown("## Choisissez le mode d'analyse")

col1, col2 = st.columns(2)
with col1:
    if st.button("Explorer les communes"):
        st.session_state.mode_ademe = "explorer"
with col2:
    if st.button("Comparer deux communes"):
        st.session_state.mode_ademe = "comparer"

# Si aucun mode choisi
if "mode_ademe" not in st.session_state:
    st.session_state.mode_ademe = None

if not st.session_state.mode_ademe:
    st.info("Sélectionnez un mode ci-dessus pour continuer.")
    st.stop()

st.markdown("---")

# ====================================================
# 🟢 MODE 1 : EXPLORER
# ====================================================
if st.session_state.mode_ademe == "explorer":
    communes_sel = st.multiselect(
        "Sélectionnez une ou plusieurs communes à explorer :",
        communes_df["nom_commune_ban"].unique(),
        default=None,
        placeholder="Ex : Lyon, Villeurbanne, Annecy..."
    )

    # On initialise un espace mémoire dans la session
    if "df_all" not in st.session_state:
        st.session_state.df_all = None

    # === Étape 1 : Chargement des données depuis l'API ADEME ===
    if communes_sel and st.button("Rechercher les DPE", use_container_width=True):
        all_df = []
        with st.spinner(f"Récupération en temps réel des DPE via l’API officielle de l’ADEME ({len(communes_sel)} communes)..."):
            for c in communes_sel:
                try:
                    df_api = fetch_dpe_by_commune(c)
                    if not df_api.empty:
                        df_api = preprocess_dpe_api(df_api)
                        df_api["commune_recherchee"] = c
                        all_df.append(df_api)
                except Exception as e:
                    st.warning(f"Erreur pour {c} : {e}")

        if all_df:
            st.session_state.df_all = pd.concat(all_df, ignore_index=True)
            st.success(f"{len(st.session_state.df_all):,} logements récupérés sur {len(communes_sel)} communes.")
        else:
            st.warning("Aucune donnée trouvée pour ces communes.")
            st.session_state.df_all = None

    # === Étape 2 : Interface interactive une fois les données chargées ===
    if st.session_state.df_all is not None:
        df_all = st.session_state.df_all.copy()

        # Ajout du jitter pour l'affichage
        df_all["lat_jitter"] = df_all["lat"] + np.random.uniform(-0.0005, 0.0005, size=len(df_all))
        df_all["lon_jitter"] = df_all["lon"] + np.random.uniform(-0.0005, 0.0005, size=len(df_all))

        # --- Filtres interactifs et dynamiques ---
        st.markdown("#### Filtres interactifs")

        # ① Filtres principaux : communes
        communes_filter = st.multiselect(
            "Commune :",
            sorted(df_all["nom_commune_ban"].dropna().unique()),
            default=sorted(df_all["nom_commune_ban"].dropna().unique()),
            key="commune_filter"
        )

        # On restreint le DF aux communes sélectionnées AVANT de construire les autres filtres
        df_subset = df_all[df_all["nom_commune_ban"].isin(communes_filter)].copy()

        # ② Filtres dépendants (dynamiques)
        col1, col2, col3 = st.columns(3)

        with col1:
            type_batiment = st.multiselect(
                "Type de bâtiment :",
                sorted(df_subset["type_batiment"].dropna().unique()),
                default=sorted(df_subset["type_batiment"].dropna().unique()),
                key="type_bat"
            )

            conso_min, conso_max = float(df_subset["conso_m2"].min()), float(df_subset["conso_m2"].max())
            conso_range = st.slider(
                "Consommation (kWh/m²/an)",
                min_value=conso_min,
                max_value=conso_max,
                value=(conso_min, conso_max),
                key="conso_range"
            )

        with col2:
            etiquettes_filter = st.multiselect(
                "Étiquette DPE :",
                sorted(df_subset["etiquette_dpe"].dropna().unique()),
                default=sorted(df_subset["etiquette_dpe"].dropna().unique()),
                key="etiquettes_filter"
            )

            cout_min, cout_max = float(df_subset["cout_m2"].min()), float(df_subset["cout_m2"].max())
            cout_range = st.slider(
                "Coût (€ / m²)",
                min_value=cout_min,
                max_value=cout_max,
                value=(cout_min, cout_max),
                key="cout_range"
            )

        with col3:
            codes_postaux_filter = st.multiselect(
                "Code postal :",
                sorted(df_subset["code_postal_ban"].dropna().unique()),
                default=sorted(df_subset["code_postal_ban"].dropna().unique()),
                key="codes_postaux"
            )

        # ④ Filtre date (manuel)
        min_date = pd.to_datetime(df_subset["date_reception_dpe"], errors="coerce").min()
        max_date = pd.to_datetime(df_subset["date_reception_dpe"], errors="coerce").max()
        col_d1, col_d2 = st.columns([3, 1])
        with col_d1:
            date_range = st.date_input(
                "Plage de dates :",
                value=(min_date.date(), max_date.date())
                if pd.notna(min_date) and pd.notna(max_date)
                else (datetime(2021, 1, 1).date(), datetime.now().date()),
                key="date_range_filter"
            )
        with col_d2:
            apply_date = st.button("Valider la plage", use_container_width=True)

        # --- Application des filtres ---
        df_filtered = df_subset[
            df_subset["type_batiment"].isin(type_batiment)
            & df_subset["etiquette_dpe"].isin(etiquettes_filter)
            & df_subset["code_postal_ban"].isin(codes_postaux_filter)
            & df_subset["conso_m2"].between(conso_range[0], conso_range[1])
            & df_subset["cout_m2"].between(cout_range[0], cout_range[1])
        ].copy()

        if apply_date and isinstance(date_range, (list, tuple)) and len(date_range) == 2:
            start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
            mask_date = df_filtered["date_reception_dpe"].between(start, end, inclusive="both")
            df_filtered = df_filtered[mask_date]

        # --- Affichage résultats ---
        st.markdown(f"### Résultats filtrés : **{len(df_filtered):,} logements**")

        center, zoom = compute_center_zoom(df_filtered)
        fig = px.scatter_mapbox(
            df_filtered,
            lat="lat_jitter", lon="lon_jitter",
            color="etiquette_dpe",
            color_discrete_map=dict(df_filtered.groupby("etiquette_dpe")["color_dpe"].first()),
            category_orders={"etiquette_dpe": ["A", "B", "C", "D", "E", "F", "G"]},  
            hover_name="nom_commune_ban",
            hover_data=[
                "type_batiment", "surface_habitable_logement",
                "conso_m2", "cout_m2", "date_reception_dpe"
            ],
            height=650, zoom=zoom,
            title="Carte des logements ADEME filtrés"
        )

        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox_center=center,
            margin=dict(l=0, r=0, t=40, b=0)
        )

        st.plotly_chart(fig, use_container_width=True)

        # --- Données + Export ---
        with st.expander("Voir les données filtrées et exporter"):
            st.dataframe(df_filtered, use_container_width=True, height=400)
            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                st.download_button(
                    "Télécharger les données filtrées (CSV)",
                    data=df_filtered.to_csv(index=False).encode("utf-8"),
                    file_name="dpe_ademe_filtre.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with c2:
                buf = BytesIO()
                fig.write_image(buf, format="png", scale=2)
                st.download_button(
                    "Télécharger la carte (PNG)",
                    data=buf.getvalue(),
                    file_name="carte_dpe_filtre.png",
                    mime="image/png",
                    use_container_width=True
                )


# ====================================================
# 🟣 MODE 2 : COMPARER
# ====================================================
if st.session_state.mode_ademe == "comparer":
    st.markdown("#### Comparaison entre deux communes")
    col_a, col_b = st.columns(2)
    with col_a:
        commune_1 = st.selectbox("Commune A :", communes_df["nom_commune_ban"].unique(), key="c1")
    with col_b:
        commune_2 = st.selectbox("Commune B :", communes_df["nom_commune_ban"].unique(), key="c2")

    # Sélection de la plage de dates
    st.markdown("###### Période à comparer")
    today = datetime.today().date()
    start_default = datetime(today.year - 1, 1, 1).date()
    date_range = st.date_input(
        "Choisissez la période de réception des DPE :",
        value=(start_default, today),
        max_value=today,
        key="compare_dates"
    )

    # === Initialisation session_state ===
    if "rapport_data" not in st.session_state:
        st.session_state.rapport_data = None
        st.session_state.date_range = None

    # === Étape 1 : Comparer ===
    if commune_1 and commune_2 and st.button("Comparer les deux communes", use_container_width=True):
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        cols = st.columns(2)
        rapport_data = []

        for i, (c, col) in enumerate(zip([commune_1, commune_2], cols)):
            with col:
                with st.spinner(f"Chargement des DPE de **{c}** en temps réel via l’API officielle de l’ADEME..."):
                    try:
                        df_api = fetch_dpe_by_commune(c)
                        if df_api.empty:
                            st.warning(f"Aucune donnée pour {c}")
                            continue

                        df_api = preprocess_dpe_api(df_api)
                        df_api = df_api[df_api["date_reception_dpe"].between(start, end, inclusive="both")].copy()
                        if df_api.empty:
                            st.info(f"Aucun nouveau logement pour {c} sur la période sélectionnée.")
                            continue

                        df_api["lat_jitter"] = df_api["lat"] + np.random.uniform(-0.0005, 0.0005, size=len(df_api))
                        df_api["lon_jitter"] = df_api["lon"] + np.random.uniform(-0.0005, 0.0005, size=len(df_api))

                        nb_logements = len(df_api)
                        mean_conso = df_api["conso_m2"].mean()
                        mean_cout = df_api["cout_m2"].mean()
                        dpe_majoritaire = (
                            df_api["etiquette_dpe"].mode()[0]
                            if not df_api["etiquette_dpe"].isna().all()
                            else "N/A"
                        )

                        # === Affichage structuré 2x2 ===
                        st.markdown(f"### {c}")
                        m1, m2 = st.columns(2)
                        m3, m4 = st.columns(2)
                        m1.metric("🏠 Nouveaux logements", f"{nb_logements:,}")
                        m2.metric("🏷️ DPE dominant", dpe_majoritaire)
                        m3.metric("⚡ Conso moyenne", f"{mean_conso:.1f} kWh/m²/an")
                        m4.metric("💰 Coût moyen", f"{mean_cout:.1f} €/m²/an")

                        # === Carte ===
                        center, zoom = compute_center_zoom(df_api)
                        fig = px.scatter_mapbox(
                            df_api,
                            lat="lat_jitter",
                            lon="lon_jitter",
                            color="etiquette_dpe",
                            color_discrete_map=dict(df_api.groupby("etiquette_dpe")["color_dpe"].first()),
                            hover_name="nom_commune_ban",
                            hover_data=["surface_habitable_logement", "conso_m2", "cout_m2", "date_reception_dpe"],
                            height=600,
                            zoom=zoom,
                            title=f"{c} – {nb_logements} logements ({start.date()} → {end.date()})"
                        )
                        fig.update_layout(
                            mapbox_style="open-street-map",
                            mapbox_center=center,
                            margin=dict(l=0, r=0, t=40, b=0),
                            hoverlabel=dict(bgcolor="white", font_size=12)
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        # === Sauvegarde temporaire pour PDF ===
                        img_path = Path(tempfile.gettempdir()) / f"carte_{c}.png"
                        fig.write_image(img_path, scale=2)

                        rapport_data.append({
                            "commune": c,
                            "stats": {"nb": nb_logements, "dpe": dpe_majoritaire, "conso": mean_conso, "cout": mean_cout},
                            "img_path": img_path,
                            "df": df_api
                        })

                    except Exception as e:
                        st.error(f"Erreur pour {c} : {e}")

        # on sauvegarde dans la session pour éviter de perdre au refresh
        if rapport_data:
            st.session_state.rapport_data = rapport_data
            st.session_state.date_range = (start, end)
            st.success("Données prêtes pour le rapport PDF.")

    # === Étape 2 : Génération du rapport complet ZIP ===
    if st.session_state.rapport_data:
        st.markdown("---")
        st.info("Vous pouvez maintenant télécharger le rapport complet (PDF + données Excel).")

        # Générer le PDF
        pdf_path = generate_pdf_report(st.session_state.rapport_data, st.session_state.date_range)

        # Créer le ZIP en mémoire
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            # Ajouter le rapport PDF
            zipf.write(pdf_path, arcname="rapport_comparatif_dpe.pdf")

            # Ajouter les fichiers Excel (un par commune)
            for data in st.session_state.rapport_data:
                commune = data["commune"]
                df = data.get("df")

                if isinstance(df, pd.DataFrame) and not df.empty:
                    cols = [
                        "nom_commune_ban",
                        "type_batiment",
                        "date_reception_dpe",
                        "code_postal_ban",
                        "surface_habitable_logement",
                        "etiquette_dpe",
                        "conso_m2",
                        "cout_m2",
                    ]
                    df = df[[c for c in cols if c in df.columns]]
                    xlsx_buf = io.BytesIO()
                    df.to_excel(xlsx_buf, index=False)
                    xlsx_buf.seek(0)
                    zipf.writestr(f"dpe_{commune}.xlsx", xlsx_buf.getvalue())

        zip_buffer.seek(0)

        # Bouton unique de téléchargement ZIP
        st.download_button(
            "Télécharger le rapport complet (ZIP)",
            data=zip_buffer,
            file_name=f"rapport_dpe_complet_{commune_1}_{commune_2}.zip",
            mime="application/zip",
            use_container_width=True,
            key="dl_zip_ready"
        )