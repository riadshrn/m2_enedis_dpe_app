import streamlit as st
from pathlib import Path

# Configuration de la page
st.set_page_config(
    page_title="DPE Rhône 69 | Analyse & Prédiction",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chargement du CSS
def load_css():
    css_file = Path(__file__).parent / "assets" / "styles.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ==================== SIDEBAR ====================
st.sidebar.markdown("""
<div style='text-align: center; padding: 1rem 0 2rem 0;'>
    <h1 style='color: white; font-size: 1.8rem; margin: 0;'>🏡 DPE Rhône 69</h1>
    <p style='color: rgba(255,255,255,0.8); font-size: 0.9rem; margin-top: 0.5rem;'>Analyse & Prédiction Énergétique</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='color: rgba(255,255,255,0.7); font-size: 0.85rem; padding: 1rem;'>
    <p><strong>Sources de données:</strong></p>
    <p>• ADEME DPE<br>• Enedis (Rhône 69)</p>
    <p style='margin-top: 1rem;'><strong>Technologies:</strong></p>
    <p>• FastAPI + Mistral AI<br>• Streamlit + Plotly</p>
</div>
""", unsafe_allow_html=True)

# ==================== PAGE ACCUEIL ====================
st.markdown("""
<div class="main-header fade-in">
    <h1>🏡 Diagnostic de Performance Énergétique</h1>
    <p>Département du Rhône (69) | Données ADEME & Enedis</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card fade-in">
        <div class="metric-value">📊</div>
        <div class="metric-label">Exploration</div>
        <p style='margin-top: 1rem; color: #666;'>Visualisez les données énergétiques locales</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card fade-in">
        <div class="metric-value">🔮</div>
        <div class="metric-label">Prédiction</div>
        <p style='margin-top: 1rem; color: #666;'>Estimez votre DPE avec l'IA</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card fade-in">
        <div class="metric-value">🤖</div>
        <div class="metric-label">Interprétation</div>
        <p style='margin-top: 1rem; color: #666;'>Comprenez vos résultats avec Mistral</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

st.markdown("### 🎯 À propos du projet")

st.markdown("""
Cette application universitaire combine **données publiques** et **intelligence artificielle** pour démocratiser 
l'accès à l'information énergétique dans le département du Rhône.

**Fonctionnalités principales:**

- 📈 **Visualisation interactive** des consommations énergétiques par commune
- 🏠 **Prédiction automatique** de l'étiquette DPE de votre logement
- ⚡ **Estimation** de la consommation énergétique (kWh/m²/an et MWh/an)
- 🤖 **Interprétation intelligente** générée par Mistral AI avec conseils personnalisés
- 🗺️ **Comparaison** avec les moyennes communales du Rhône

---
""")

st.info("👈 Utilisez le menu latéral pour naviguer entre les sections.")