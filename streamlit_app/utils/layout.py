import streamlit as st
from pathlib import Path
import base64

def load_css():
    """Charge les styles CSS globaux."""
    css_file = Path(__file__).parent.parent / "assets" / "styles.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_sidebar():
    """Affiche une barre latérale cohérente et illustrée sur toutes les pages."""
    logo_path = Path(__file__).parent.parent / "assets" / "logo-removebg.png"

    # Encoder le logo en base64 pour affichage inline
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode()
        logo_html = f"""
        <div style='text-align: center; margin-bottom: 1rem;'>
            <div style="
                display:inline-block;
                background-color:white;
                border-radius:12px;
                padding:8px 10px;
                box-shadow:0 2px 8px rgba(0,0,0,0.25);
                transition: all 0.3s ease;
            ">
                <img src="data:image/png;base64,{logo_base64}" 
                     alt="Logo DPE Vision AI"
                     width="110"
                     style="display:block;margin:auto;"/>
            </div>
        </div>
        """
    else:
        logo_html = ""

    # Bloc principal du header dans la sidebar
    st.sidebar.markdown(f"""
    {logo_html}
    <div style='text-align: center; padding-bottom: 1.5rem;'>
        <h1 style='color: #f0f0f0; font-size: 1.6rem; margin: 0;'>DPE Vision AI</h1>
        <p style='color: rgba(255,255,255,0.8); font-size: 0.9rem; margin-top: 0.3rem;'>
            Analyse & Prédiction Énergétique
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Séparateur
    st.sidebar.markdown("<hr style='border-color:rgba(255,255,255,0.2);margin:1rem 0;'>", unsafe_allow_html=True)

    # Bloc d’infos contextuelles
    st.sidebar.markdown("""
    <div style='color: rgba(255,255,255,0.9); font-size: 0.85rem; padding: 0 0.5rem;'>
        <p><strong>Sources de données :</strong></p>
        <ul style='margin-left: -1rem;'>
            <li>ADEME – Diagnostics DPE</li>
            <li>Enedis – Consommations du Rhône (69)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
