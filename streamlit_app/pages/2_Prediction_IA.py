import streamlit as st
from pathlib import Path
import sys
import time

# === Imports internes ===
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.api_utils import call_api
from utils.dpe_utils import display_dpe_badge, create_dpe_gauge

# === Configuration ===
st.set_page_config(page_title="Prédiction IA | DPE Rhône 69", page_icon="🔮", layout="wide")

# === CSS ===
def load_css():
    css_file = Path(__file__).parent.parent / "assets" / "styles.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css()

# === Initialisation session_state ===
if "prediction" not in st.session_state:
    st.session_state.prediction = {}
if "last_interpret_time" not in st.session_state:
    st.session_state.last_interpret_time = 0
if "mode_pred" not in st.session_state:
    st.session_state.mode_pred = None  # "simple" ou "complet"

# === HEADER ===
st.markdown("""
<div class="main-header fade-in">
    <h1>🔮 Prédiction DPE & Interprétation IA</h1>
    <p>Estimez la performance énergétique de votre logement avec ou sans IA complète</p>
</div>
""", unsafe_allow_html=True)

# === CHOIX DU MODE ===
st.markdown("## ⚙️ Choisissez le type de prédiction")

col1, col2 = st.columns(2)
with col1:
    if st.button("🏠 Prédire uniquement à partir des caractéristiques"):
        st.session_state.mode_pred = "simple"
with col2:
    if st.button("⚡ Prédire avec consommation (renseignée ou prédite) + interprétation IA"):
        st.session_state.mode_pred = "complet"

if not st.session_state.mode_pred:
    st.info("➡️ Sélectionnez un mode ci-dessus pour continuer.")
    st.stop()

# === FORMULAIRE ===
st.markdown("---")
st.markdown("### 🏡 Informations sur le logement")

commune = st.text_input("Commune (Rhône)", value="Lyon")

col1, col2 = st.columns(2)
with col1:
    surface_habitable_logement = st.number_input("Surface habitable (m²)", 10, 500, 100)
    hauteur_sous_plafond = st.number_input("Hauteur sous plafond (m)", 2.0, 4.0, 2.6)
    nombre_niveau_logement = st.number_input("Nombre de niveaux", 1, 5, 1)
    anciennete = st.number_input("Ancienneté du bâtiment (en années)", 0, 200, 15)
    isolation_toiture = st.selectbox("Isolation toiture", ["0", "1"])

with col2:
    score_isolation_moyen = st.number_input("Score d’isolation moyen (0 à 1)", 0.0, 1.0, 1.0)
    qualite_isolation_murs = st.selectbox("Qualité isolation murs", ["très bonne", "bonne", "moyenne", "insuffisante"])
    qualite_isolation_menuiseries = st.selectbox("Qualité isolation menuiseries", ["très bonne", "bonne", "moyenne", "insuffisante"])
    type_energie_principale_chauffage = st.selectbox("Énergie principale de chauffage", ["gaz", "électricité", "fioul", "bois", "pompe à chaleur"])
    type_logement_source = st.selectbox("Type de logement", ["maison", "appartement"])

st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    energie_regroupee = st.selectbox("Énergie regroupée", ["gaz_naturel", "electrique", "bois", "fioul"])
    classe_annee_construction = st.selectbox("Classe d’année de construction", [
        "avant_1948", "1949_1974", "1975_1989", "1990_1999", "2000_2010", "apres_2012"
    ])
with col2:
    knows_conso = False
    conso_m2 = 0.0
    if st.session_state.mode_pred == "complet":
        knows_conso = st.toggle("Je connais ma consommation énergétique (kWh/m²/an)")
        conso_m2 = st.number_input("Consommation (kWh/m²/an)", 0.0, 1000.0, 6.0, disabled=not knows_conso)

# === JSON de base ===
volume_logement = surface_habitable_logement * hauteur_sous_plafond
base_data = {
    "volume_logement": volume_logement,
    "hauteur_sous_plafond": hauteur_sous_plafond,
    "nombre_niveau_logement": nombre_niveau_logement,
    "anciennete": anciennete,
    "isolation_toiture": isolation_toiture,
    "score_isolation_moyen": score_isolation_moyen,
    "qualite_isolation_murs": qualite_isolation_murs,
    "qualite_isolation_menuiseries": qualite_isolation_menuiseries,
    "type_energie_principale_chauffage": type_energie_principale_chauffage,
    "energie_regroupee": energie_regroupee,
    "type_logement_source": type_logement_source,
    "classe_annee_construction": classe_annee_construction,
    "surface_habitable_logement": surface_habitable_logement,
    "nom_commune": commune
}

# === MODE SIMPLE (DPE sans conso) ===
if st.session_state.mode_pred == "simple":
    st.markdown("---")
    st.markdown("### 🎯 Prédiction DPE à partir des caractéristiques du logement")

    if st.button("🚀 Prédire uniquement l'étiquette DPE", use_container_width=True):
        with st.spinner("Calcul en cours..."):
            result = call_api("/predict/dpe_sans_conso", base_data)

            if result:
                etiquette = result.get("etiquette_dpe", "N/A")
                st.session_state.prediction = {
                    "etiquette": etiquette,
                    "mode": "simple"
                }

                st.success(f"✅ Étiquette prédite : **{etiquette}** (basée uniquement sur les caractéristiques)")
                st.markdown(display_dpe_badge(etiquette), unsafe_allow_html=True)
                st.plotly_chart(create_dpe_gauge(etiquette), use_container_width=True)
    st.stop()  # pas d’interprétation pour ce mode

# === MODE COMPLET ===
st.markdown("---")
st.markdown("### 🎯 Prédiction énergétique (avec conso + interprétation)")

if st.button("🚀 Lancer la prédiction IA complète", use_container_width=True):
    with st.spinner("Analyse en cours..."):
        if knows_conso:
            data = base_data.copy()
            data["conso_m2"] = conso_m2
            result = call_api("/predict/dpe_avec_conso", data)
        else:
            result = call_api("/predict/dpe_auto", base_data)

        if result:
            etiquette = result.get("etiquette_dpe", "N/A")
            conso_predite = result.get("conso_m2_predite", conso_m2)
            st.session_state.prediction = {
                "etiquette": etiquette,
                "conso_m2": conso_predite,
                "mode": "complet"
            }

# === AFFICHAGE PERSISTANT ===
pred = st.session_state.prediction
if pred and pred.get("mode") in ["simple", "complet"]:
    st.markdown("---")
    st.markdown("### 📊 Résumé de la dernière prédiction")

    etiquette = pred.get("etiquette", "N/A")
    conso_val = pred.get("conso_m2", None)
    mode_pred = pred.get("mode")

    if mode_pred == "simple":
        st.info("🧱 Prédiction réalisée à partir des **caractéristiques uniquement**.")
    elif mode_pred == "complet":
        st.info("⚡ Prédiction réalisée avec **consommation renseignée ou estimée par l’IA**.")

    st.success(f"✅ Étiquette DPE prédite : **{etiquette}**")

    if conso_val is not None:
        st.metric("Consommation utilisée", f"{conso_val:.2f} kWh/m²/an")

    st.markdown(display_dpe_badge(etiquette), unsafe_allow_html=True)
    st.plotly_chart(create_dpe_gauge(etiquette), use_container_width=True)

# === INTERPRÉTATION ===
st.markdown("---")
st.markdown("### 🤖 Interprétation par Mistral AI")

if not pred or pred.get("mode") != "complet":
    st.info("ℹ️ Lancez d’abord une prédiction complète avant de demander une interprétation.")
    st.stop()

now = time.time()
remaining = 15 - (now - st.session_state.last_interpret_time)

if remaining > 0:
    st.warning(f"⏳ Veuillez patienter encore {remaining:.1f} secondes avant de relancer une interprétation.")
    st.progress((15 - remaining) / 15)
    st.stop()

if st.button("🧠 Générer l’interprétation détaillée", use_container_width=True, type="primary"):
    st.session_state.last_interpret_time = time.time()

    with st.spinner("Mistral analyse votre logement..."):
        try:
            interpretation_data = {
                **base_data,
                "conso_m2": pred["conso_m2"],
                "etiquette_dpe_regroupee": pred["etiquette"],
                "nom_commune": commune
            }

            result = call_api("/interpretation", interpretation_data)

            if result:
                interpretation = result.get("interpretation", "")
                commune_res = result.get("commune", "")
                conso_totale = result.get("conso_totale_mwh", None)
                prompt_envoye = result.get("prompt_envoye", "")

                st.success(f"✅ Interprétation générée pour **{commune_res or commune}**")

                if conso_totale:
                    st.metric("Consommation totale estimée", f"{conso_totale:.2f} MWh/an")

                with st.expander("🧩 Voir le prompt envoyé à Mistral"):
                    st.code(prompt_envoye, language="markdown")

                st.markdown("### 🧠 Interprétation du modèle")
                st.markdown(interpretation, unsafe_allow_html=False)

        except Exception as e:
            if "429" in str(e):
                st.error("⚠️ Trop de requêtes envoyées à Mistral AI. Patientez quelques secondes avant de réessayer.")
            else:
                st.error(f"❌ Erreur lors de l'interprétation : {e}")
