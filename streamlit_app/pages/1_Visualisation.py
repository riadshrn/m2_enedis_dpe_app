import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Ajouter le dossier parent au path pour importer utils
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.dpe_utils import DPE_COLORS

# Configuration
st.set_page_config(
    page_title="Visualisation | DPE Rhône 69",
    page_icon="📊",
    layout="wide"
)

# Chargement du CSS
def load_css():
    css_file = Path(__file__).parent.parent / "assets" / "styles.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ==================== PAGE ====================
st.markdown("""
<div class="main-header fade-in">
    <h1>📊 Exploration des Données Énergétiques</h1>
    <p>Département du Rhône (69)</p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "📁 Charger le fichier CSV (df_enedis_69.csv)",
    type=['csv'],
    help="Chargez votre dataset pour visualiser les données"
)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        
        st.success(f"✅ Dataset chargé: {len(df):,} logements")
        
        tab1, tab2, tab3 = st.tabs(["📈 Statistiques", "🗺️ Carte", "📊 Distributions"])
        
        with tab1:
            st.markdown("### 📊 Vue d'ensemble")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🏠 Logements", f"{len(df):,}")
            
            with col2:
                if 'Etiquette_DPE' in df.columns:
                    mode_dpe = df['Etiquette_DPE'].mode()[0] if not df['Etiquette_DPE'].mode().empty else "N/A"
                    st.metric("🏆 DPE Modal", mode_dpe)
            
            with col3:
                if 'Conso_5_usages_é_finale' in df.columns:
                    avg_conso = df['Conso_5_usages_é_finale'].mean()
                    st.metric("⚡ Conso. Moyenne", f"{avg_conso:.0f} kWh/m²")
            
            with col4:
                if 'Commune' in df.columns:
                    nb_communes = df['Commune'].nunique()
                    st.metric("🏘️ Communes", nb_communes)
            
            st.markdown("---")
            
            if 'Etiquette_DPE' in df.columns:
                st.markdown("### 🎨 Répartition des étiquettes DPE")
                
                dpe_counts = df['Etiquette_DPE'].value_counts().sort_index()
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=dpe_counts.index,
                        y=dpe_counts.values,
                        marker=dict(
                            color=[DPE_COLORS.get(label, '#999') for label in dpe_counts.index]
                        ),
                        text=dpe_counts.values,
                        textposition='auto',
                    )
                ])
                
                fig.update_layout(
                    title="Distribution des étiquettes DPE",
                    xaxis_title="Étiquette DPE",
                    yaxis_title="Nombre de logements",
                    height=400,
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.markdown("### 🗺️ Cartographie (à implémenter)")
            st.info("💡 Intégration future: carte interactive Folium/Plotly avec moyennes par commune")
            
            if 'Commune' in df.columns and 'Conso_5_usages_é_finale' in df.columns:
                commune_stats = df.groupby('Commune')['Conso_5_usages_é_finale'].mean().sort_values(ascending=False).head(10)
                
                fig = px.bar(
                    x=commune_stats.values,
                    y=commune_stats.index,
                    orientation='h',
                    title="Top 10 communes - Consommation moyenne",
                    labels={'x': 'kWh/m²/an', 'y': 'Commune'},
                    color=commune_stats.values,
                    color_continuous_scale=['#009966', '#FFCC00', '#FF0000']
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.markdown("### 📊 Distributions")
            
            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
            
            if len(numeric_cols) > 0:
                selected_col = st.selectbox("Sélectionnez une variable", numeric_cols)
                
                fig = px.histogram(
                    df,
                    x=selected_col,
                    nbins=50,
                    title=f"Distribution: {selected_col}",
                    color_discrete_sequence=['#009966']
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement: {str(e)}")

else:
    st.info("👆 Chargez un fichier CSV pour commencer l'exploration")