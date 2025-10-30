import streamlit as st
from pathlib import Path

def load_css():
    css_file = Path(__file__).parent.parent / "assets" / "styles.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def render_sidebar():
    """Affiche une barre latérale cohérente sur toutes les pages"""
    st.sidebar.markdown("""
    <div style='text-align: center; padding: 1rem 0 2rem 0;'>
        <h1 style='color: #f0f0f0; font-size: 1.8rem; margin: 0;'>🏡 DPE Rhône 69</h1>
        <p style='color: rgba(255,255,255,0.75); font-size: 0.9rem; margin-top: 0.4rem;'>Analyse & Prédiction Énergétique</p>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("---")

    st.sidebar.markdown("""
    <div style='color: rgba(255,255,255,0.8); font-size: 0.85rem; padding: 0 1rem;'>
        <p><strong>Sources de données :</strong></p>
        <ul style='margin-left: -1rem;'>
            <li>ADEME (DPE)</li>
            <li>Enedis (Rhône 69)</li>
        </ul>
        <p style='margin-top: 1rem;'><strong>Technologies :</strong></p>
        <ul style='margin-left: -1rem;'>
            <li>FastAPI + Mistral AI</li>
            <li>Streamlit + Plotly</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
