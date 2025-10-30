import streamlit as st
from pathlib import Path
from utils.layout import render_sidebar, load_css

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
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card fade-in" style="text-align:center;">
        <div style='font-size:2.5rem;'>📊</div>
        <div style='font-weight:bold;font-size:1.2rem;'>Exploration & Visualisation</div>
        <p style='margin-top:0.5rem;color:#666;'>
            Explorez les données énergétiques du Rhône, identifiez les tendances et 
            <strong>assemblez des dashboards interactifs</strong> pour une analyse complète.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card fade-in" style="text-align:center;">
        <div style='font-size:2.5rem;'>🔮</div>
        <div style='font-weight:bold;font-size:1.2rem;'>Prédiction & Interprétation</div>
        <p style='margin-top:0.5rem;color:#666;'>
            Estimez automatiquement <strong>l’étiquette DPE</strong> et la 
            <strong>consommation énergétique</strong> grâce à l’IA
            & obtenez une <strong>interprétation</strong> via un modèle LLM.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card fade-in" style="text-align:center;">
        <div style='font-size:2.5rem;'>🧠</div>
        <div style='font-weight:bold;font-size:1.2rem;'>AutoML & Réentraînement</div>
        <p style='margin-top:0.5rem;color:#666;'>
            <strong>Réentraînez un modèle existant</strong> avec des nouvelles données 
            & utilisez l’outil <strong>AutoML</strong> pour 
            <strong>comparer plusieurs algorithmes</strong> pour une modélisation.
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
    - **Comparaison géographique** entre communes, zones climatiques et types d’énergie utilisés.  
    - Centrage automatique sur le département du Rhône avec ajustement dynamique du zoom.  
    """)

with st.expander("Prédiction automatisée du DPE"):
    st.markdown("""
    - Modèle **RandomForest** entraîné sur des données locales.  
    - Double prédiction :
      -  **Étiquette DPE estimée** (A à G)  
      -  **Consommation énergétique prévisionnelle** (kWh/m²/an).  
    - Interface simple : saisie manuelle ou import CSV.  
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

