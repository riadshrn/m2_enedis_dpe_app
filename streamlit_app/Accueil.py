import streamlit as st
from pathlib import Path
from utils.layout import render_sidebar, load_css
import base64
import re

logo_path = Path(__file__).parent.parent / "assets" / "logo-removebg.png"

# ==================== CONFIGURATION GLOBALE ====================
st.set_page_config(
    page_title="DPE Vision AI – Analyse et Prédiction DPE",
    page_icon=logo_path,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Charger les styles et la sidebar commune
load_css()
render_sidebar()

# ==================== PAGE D’ACCUEIL ====================
st.markdown("""
<div class="main-header fade-in" style="text-align:center;">
    <h1>DPE Vision AI</h1>
    <p style="font-size:1.2rem;">Analyse, visualisation et prédiction du Diagnostic de Performance Énergétique (DPE)</p>
    <p style="color:white;">Données ADEME & Enedis – Département du Rhône (69)</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ==================== CARTES D’APERÇU ====================
col1, col2, col3, col4 = st.columns(4)

# --- Exploration & Visualisation ---
with col1:
    st.markdown("""
    <div class="metric-card fade-in" style="text-align:center;">
        <div style='font-size:2.5rem;'>📊</div>
        <div style='font-weight:bold;font-size:1.2rem;'>Exploration & Visualisation</div>
        <p style='margin-top:0.5rem;color:#666;'>
            Explorez les <strong>données énergétiques du Rhône</strong>, identifiez les tendances et 
            construisez des <strong>dashboards interactifs</strong> pour une analyse complète.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ---  Cartographie & Données ADEME ---
with col2:
    st.markdown("""
    <div class="metric-card fade-in" style="text-align:center;">
        <div style='font-size:2.5rem;'>🗺️</div>
        <div style='font-weight:bold;font-size:1.2rem;'>Cartographie & Données ADEME</div>
        <p style='margin-top:0.5rem;color:#666;'>
            Visualisez les <strong>logements du Rhône</strong> via la cartographie dynamique.  
            Comparez les <strong>communes</strong> en temps réel via l’<strong>API ADEME</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ---  Prédiction & Interprétation ---
with col3:
    st.markdown("""
    <div class="metric-card fade-in" style="text-align:center;">
        <div style='font-size:2.5rem;'>🔮</div>
        <div style='font-weight:bold;font-size:1.2rem;'>Prédiction & Interprétation</div>
        <p style='margin-top:0.5rem;color:#666;'>
            Prédisez automatiquement <strong>l’étiquette DPE</strong> et la 
            <strong>consommation énergétique</strong> d’un logement.  
            Profitez d’une <strong>interprétation intelligente</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ---  AutoML & Réentraînement ---
with col4:
    st.markdown("""
    <div class="metric-card fade-in" style="text-align:center;">
        <div style='font-size:2.5rem;'>🧠</div>
        <div style='font-weight:bold;font-size:1.2rem;'>AutoML & Réentraînement</div>
        <p style='margin-top:0.5rem;color:#666;'>
            <strong>Réentraînez notre modèle</strong> avec de nouvelles données, comparez les 
            <strong>algorithmes</strong> les plus performants et générez un 
            <strong>rapport complet AutoML</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==================== SECTION À PROPOS ====================
st.markdown("### À propos du projet")

st.markdown("""
**DPE Vision AI** est une application combinant 
**<span style="color:#008000;">données énergétiques publiques</span>** et 
**<span style="color:#003366;">intelligence artificielle</span>**, afin de rendre accessible l’analyse énergétique du parc immobilier du Rhône.
""", unsafe_allow_html=True)


st.markdown("### Fonctionnalités principales")

with st.expander("Exploration et tableaux de bord interactifs"):
    st.markdown("""
    - Visualisation dynamique des **indicateurs énergétiques du Rhône (69)** à partir des données ADEME et Enedis.  
    - **Dashboard complet** avec filtres multi-critères : commune, type de bâtiment, année de construction, etc.  
    - Indicateurs clés : consommation moyenne, émissions GES, coût au m².  
    - **Cartes choroplèthes interactives** et graphiques exportables (CSV / HTML).  
    """)

with st.expander("Cartographie énergétique intelligente"):
    st.markdown("""
    - Carte interactive des logements et de leurs classes DPE, colorée selon l’étiquette énergétique (A → G).
    - **Filtres avancés** : commune, code postal, type de bâtiment, étiquette DPE, consommation et coût énergétique.
    - Exploration en temps réel via l’API officielle de l’ADEME, permettant d’importer automatiquement les données DPE neuves de plusieurs communes.
    - Comparaison géographique entre deux communes : visualisation côte à côte des cartes, des DPE dominants, de la consommation moyenne et du coût énergétique moyen.
    - Génération automatique d’un rapport PDF comparatif entre deux communes :
        - Inclut les cartes, les statistiques principales, et un aperçu des données utilisées,
        - Présenté en format A4 paysage avec mise en page professionnelle et logos ADEME + application.
    """)

with st.expander("Prédiction automatisée du DPE"):
    st.markdown("""
    - Modèle **RandomForest** entraîné sur des données locales (ADEME, Enedis).  
    - Triple prédiction :
      -  **Étiquette DPE estimée** Étiquette DPE estimée (A à G) basée uniquement sur les caractéristiques physiques du logement, sans utiliser la consommation réelle.
      -  **Consommation énergétique prévisionnelle** (kWh/m²/an), calculée à partir des variables structurelles et thermiques du bien.
      -  **Étiquette DPE finale**, déterminée en incluant la consommation réelle saisie par l’utilisateur ou, à défaut, celle prédite automatiquement par le modèle de consommation.           
    - Interface simple : saisie guidée.  
    - **Interprétation automatique** des résultats générée par *Mistral AI*.  
    """)

with st.expander("AutoML – Création et évaluation de modèles"):
    st.markdown("""
    - Génération automatique d’un **dataset simulé de 10 000 logements**.  
    - Entraînement et comparaison de plusieurs algorithmes :
      - Random Forest, Decision Tree, Gradient Boosting, AdaBoost, Logistic Regression, KNN, SVM.  
    - Évaluation sur des métriques robustes :
      - *Accuracy*,  *F1-score*,  *Recall*, *Précision*.  
    - Sélection et visualisation du modèle choisi (matrice de confusion, rapport détaillé).  
    - **Téléchargement du modèle entraîné** au format `.joblib`.
    - Génération automatique d’un rapport PDF complet :
        - Contient la comparaison des modèles, leurs hyperparamètres, et les matrices de confusion correspondantes
    """)

with st.expander("Réentraînement interactif des modèles"):
    st.markdown("""
    - Import ou génération d’un **nouveau jeu de données**.  
    - Réentraînement complet avec séparation *train/test* et suivi des performances.  
    - Visualisations incluses :
      - Rapport de classification (Précision, Rappel, F1 par classe).  
      - Graphique des F1-score par étiquette.  
      - **Matrice de confusion annotée** et export du modèle réentraîné.  
    """)

with st.expander("Interprétation intelligente"):
    st.markdown("""
    - Analyse textuelle des résultats de prédiction via **Mistral AI**.  
    - Explication du classement DPE et conseils d’amélioration personnalisés.  
    - Résumé clair des points forts et faibles du logement.  
    """)

with st.expander("Architecture & intégration"):
    st.markdown("""
    - **Backend :** FastAPI (API REST de prédiction et interprétation)  
    - **Frontend :** Streamlit (interface web intuitive et réactive)  
    - **Modélisation :** Scikit-Learn, Pandas, NumPy, Plotly  
    - **Déploiement :** Docker & Hugging Face Spaces  
    - **Sources :** ADEME (DPE) + Enedis (consommations énergétiques du Rhône 69)  
    """)


st.markdown("## Rapports du projet DPE Vision AI")

# --- DÉFINIR LES CHEMINS ---
rapports_dir = Path(__file__).parent / "rapports"
img_dir = Path(__file__).parent / "img"

# --- LISTE DES RAPPORTS DISPONIBLES ---
rapports = {
    "Rapport technique": "DOCUMENTATION_TECHNIQUE.md",
    "Rapport fonctionnel": "DOCUMENTATION_FONCTIONNELLE.md",
    "Rapport d’étude": "RAPPORT_ETUDE.md"
}

# --- BARRE DE BOUTONS ---
col1, col2, col3 = st.columns(3)
for i, (titre, fichier) in enumerate(rapports.items()):
    with [col1, col2, col3][i]:
        if st.button(titre, use_container_width=True):
            st.session_state.rapport_selectionne = fichier

# --- INITIALISATION ---
if "rapport_selectionne" not in st.session_state:
    st.session_state.rapport_selectionne = None

# --- AFFICHAGE DU RAPPORT SÉLECTIONNÉ ---
if st.session_state.rapport_selectionne:
    rapport_path = rapports_dir / st.session_state.rapport_selectionne

    if rapport_path.exists():
        contenu = rapport_path.read_text(encoding="utf-8")

        # --- Conversion automatique des images ---
        matches = re.findall(r'src="\.\./img/([^"]+)"', contenu)
        for filename in matches:
            img_path = img_dir / filename
            if img_path.exists():
                with open(img_path, "rb") as img_file:
                    img_base64 = base64.b64encode(img_file.read()).decode()
                contenu = contenu.replace(
                    f"../img/{filename}",
                    f"data:image/png;base64,{img_base64}"
                )
            else:
                st.warning(f"Image introuvable : {filename}")

        # --- Affichage du rapport complet ---
        st.markdown("---")
        st.markdown(f"### Rapport : **{rapport_path.stem.replace('_', ' ')}**")
        st.markdown(contenu, unsafe_allow_html=True)

    else:
        st.error(f"Le fichier {rapport_path.name} est introuvable.")
else:
    st.info("Sélectionnez un rapport à consulter ci-dessus.")