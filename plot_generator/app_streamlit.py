"""
Application Streamlit pour le générateur de graphiques Plotly
Supporte : CSV, API, et sélection interactive des colonnes
"""

import streamlit as st
import pandas as pd
import requests
from io import StringIO
import sys
sys.path.append('.')
from plotly_graph_generator import generer_graphique_plotly


# Configuration de la page
st.set_page_config(
    page_title="Générateur de Graphiques Plotly",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def charger_donnees_api(url, headers=None, params=None):
    """
    Charge des données depuis une API REST.
    
    Paramètres:
    -----------
    url : str
        URL de l'API
    headers : dict
        Headers HTTP (optionnel, pour authentification)
    params : dict
        Paramètres de requête (optionnel)
    
    Returns:
    --------
    pd.DataFrame ou None
    """
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        
        # Tenter de parser comme JSON
        try:
            data = response.json()
            
            # Si c'est une liste de dictionnaires
            if isinstance(data, list):
                return pd.DataFrame(data)
            
            # Si c'est un dictionnaire avec une clé contenant les données
            elif isinstance(data, dict):
                # Chercher la clé contenant les données
                for key in ['data', 'results', 'items', 'records', 'rows']:
                    if key in data:
                        return pd.DataFrame(data[key])
                
                # Si pas de clé standard, essayer de convertir directement
                return pd.DataFrame([data])
            
        except ValueError:
            # Si ce n'est pas du JSON, essayer CSV
            return pd.read_csv(StringIO(response.text))
        
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement depuis l'API: {str(e)}")
        return None


def charger_donnees_csv(fichier):
    """Charge des données depuis un fichier CSV uploadé."""
    try:
        return pd.read_csv(fichier)
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement du CSV: {str(e)}")
        return None


def main():
    # En-tête de l'application
    st.title("📊 Générateur de Graphiques Plotly")
    st.markdown("*Créez des visualisations interactives en quelques clics*")
    
    # Sidebar pour la configuration
    st.sidebar.header("⚙️ Configuration")
    
    # Sélection de la source de données
    source_donnees = st.sidebar.radio(
        "Source des données",
        ["📁 Fichier CSV", "🌐 API REST"],
        help="Choisissez comment charger vos données"
    )
    
    df = None
    
    # === CHARGEMENT DES DONNÉES ===
    if source_donnees == "📁 Fichier CSV":
        st.sidebar.subheader("Upload du fichier")
        fichier_csv = st.sidebar.file_uploader(
            "Choisissez un fichier CSV",
            type=['csv'],
            help="Uploadez votre fichier CSV"
        )
        
        if fichier_csv is not None:
            df = charger_donnees_csv(fichier_csv)
            if df is not None:
                st.sidebar.success(f"✅ {len(df)} lignes chargées")
    
    else:  # API REST
        st.sidebar.subheader("Configuration de l'API")
        
        url_api = st.sidebar.text_input(
            "URL de l'API",
            placeholder="https://api.example.com/data",
            help="URL complète de votre API REST"
        )
        
        # Options avancées (collapsible)
        with st.sidebar.expander("🔧 Options avancées"):
            # Headers pour authentification
            use_auth = st.checkbox("Authentification")
            headers = {}
            if use_auth:
                auth_type = st.selectbox(
                    "Type d'authentification",
                    ["Bearer Token", "API Key", "Custom Header"]
                )
                
                if auth_type == "Bearer Token":
                    token = st.text_input("Token", type="password")
                    if token:
                        headers['Authorization'] = f"Bearer {token}"
                
                elif auth_type == "API Key":
                    api_key = st.text_input("API Key", type="password")
                    key_name = st.text_input("Nom de la clé", value="X-API-Key")
                    if api_key:
                        headers[key_name] = api_key
                
                else:  # Custom Header
                    header_name = st.text_input("Nom du header")
                    header_value = st.text_input("Valeur", type="password")
                    if header_name and header_value:
                        headers[header_name] = header_value
            
            # Paramètres de requête
            use_params = st.checkbox("Paramètres de requête")
            params = {}
            if use_params:
                params_text = st.text_area(
                    "Paramètres (format: clé=valeur, un par ligne)",
                    placeholder="page=1\nlimit=100"
                )
                if params_text:
                    for line in params_text.split('\n'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            params[key.strip()] = value.strip()
        
        # Bouton pour charger les données
        if st.sidebar.button("🔄 Charger les données", type="primary"):
            if url_api:
                with st.spinner("Chargement des données depuis l'API..."):
                    df = charger_donnees_api(
                        url_api,
                        headers=headers if headers else None,
                        params=params if params else None
                    )
                    if df is not None:
                        st.sidebar.success(f"✅ {len(df)} lignes chargées")
            else:
                st.sidebar.error("❌ Veuillez entrer une URL d'API")
    
    # === APERÇU DES DONNÉES ===
    if df is not None:
        st.header("📋 Aperçu des données")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Nombre de lignes", len(df))
        col2.metric("Nombre de colonnes", len(df.columns))
        col3.metric("Mémoire utilisée", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
        
        # Afficher un aperçu
        with st.expander("👁️ Voir les données", expanded=True):
            st.dataframe(df.head(100), use_container_width=True)
        
        # Afficher les types de colonnes
        with st.expander("📊 Informations sur les colonnes"):
            col_info = pd.DataFrame({
                'Colonne': df.columns,
                'Type': df.dtypes.values,
                'Valeurs nulles': df.isnull().sum().values,
                'Valeurs uniques': [df[col].nunique() for col in df.columns]
            })
            st.dataframe(col_info, use_container_width=True)
        
        # === CONFIGURATION DU GRAPHIQUE ===
        st.header("🎨 Configuration du graphique")
        
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            # Type de graphique
            type_graphique = st.selectbox(
                "Type de graphique",
                [
                    'scatter', 'line', 'bar', 'histogram', 
                    'box', 'violin', 'pie', 'sunburst', 
                    'treemap', 'scatter_3d', 'density_heatmap', 
                    'density_contour', 'area'
                ],
                help="Sélectionnez le type de visualisation"
            )
            
            # Sélection de la colonne X
            x_colonne = st.selectbox(
                "Colonne X (abscisses) *",
                options=df.columns.tolist(),
                help="Colonne obligatoire pour l'axe des X"
            )
        
        with col_right:
            # Sélection de la colonne Y (optionnelle)
            y_colonnes = ['(Aucune)'] + df.columns.tolist()
            y_colonne = st.selectbox(
                "Colonne Y (ordonnées)",
                options=y_colonnes,
                help="Optionnel selon le type de graphique"
            )
            y_colonne = None if y_colonne == '(Aucune)' else y_colonne
            
            # Sélection de la colonne Z (faceting, optionnelle)
            z_colonnes = ['(Aucune)'] + df.columns.tolist()
            z_colonne = st.selectbox(
                "Colonne Z (faceting/segmentation)",
                options=z_colonnes,
                help="Optionnel : crée des sous-graphiques par catégorie"
            )
            z_colonne = None if z_colonne == '(Aucune)' else z_colonne
        
        # Options supplémentaires
        with st.expander("🎨 Options de personnalisation"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Colonne pour la couleur
                color_colonnes = ['(Aucune)'] + df.columns.tolist()
                color_colonne = st.selectbox(
                    "Couleur par",
                    options=color_colonnes,
                    help="Colorer les points selon une variable"
                )
                color_colonne = None if color_colonne == '(Aucune)' else color_colonne
                
                # Titre personnalisé
                titre_custom = st.text_input(
                    "Titre du graphique (optionnel)",
                    placeholder="Laissez vide pour titre automatique"
                )
            
            with col2:
                # Colonne pour la taille
                size_colonnes = ['(Aucune)'] + df.select_dtypes(include=['number']).columns.tolist()
                size_colonne = st.selectbox(
                    "Taille des points par",
                    options=size_colonnes,
                    help="Varier la taille selon une variable numérique"
                )
                size_colonne = None if size_colonne == '(Aucune)' else size_colonne
                
                # Colonnes pour hover
                hover_colonnes = st.multiselect(
                    "Infos au survol",
                    options=df.columns.tolist(),
                    help="Colonnes à afficher au survol"
                )
        
        # Bouton pour générer le graphique
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            generer = st.button(
                "🚀 Générer le graphique",
                type="primary",
                use_container_width=True
            )
        
        # === GÉNÉRATION DU GRAPHIQUE ===
        if generer:
            with st.spinner("Génération du graphique en cours..."):
                # Préparer les kwargs
                kwargs = {}
                if color_colonne:
                    kwargs['color'] = color_colonne
                if size_colonne:
                    kwargs['size'] = size_colonne
                if hover_colonnes:
                    kwargs['hover_data'] = hover_colonnes
                
                # Générer le graphique
                fig = generer_graphique_plotly(
                    df,
                    type_graphique=type_graphique,
                    x=x_colonne,
                    y=y_colonne,
                    z=z_colonne,
                    titre=titre_custom if titre_custom else None,
                    **kwargs
                )
                
                if fig is not None:
                    st.success("✅ Graphique généré avec succès !")
                    
                    # Afficher le graphique
                    st.header("📊 Résultat")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Options de téléchargement
                    st.subheader("💾 Télécharger")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # Télécharger en HTML
                        html_str = fig.to_html(include_plotlyjs='cdn')
                        st.download_button(
                            label="📄 Télécharger HTML",
                            data=html_str,
                            file_name="graphique.html",
                            mime="text/html",
                            help="Format interactif pour navigateur"
                        )
                    
                    with col2:
                        # Télécharger en PNG (si kaleido disponible)
                        try:
                            img_bytes = fig.to_image(format="png", width=1200, height=800)
                            st.download_button(
                                label="🖼️ Télécharger PNG",
                                data=img_bytes,
                                file_name="graphique.png",
                                mime="image/png",
                                help="Image statique haute qualité"
                            )
                        except Exception as e:
                            st.button(
                                "🖼️ PNG non disponible",
                                disabled=True,
                                help="Installez kaleido: pip install kaleido"
                            )
                    
                    with col3:
                        # Télécharger en PDF (si kaleido disponible)
                        try:
                            pdf_bytes = fig.to_image(format="pdf", width=1200, height=800)
                            st.download_button(
                                label="📑 Télécharger PDF",
                                data=pdf_bytes,
                                file_name="graphique.pdf",
                                mime="application/pdf",
                                help="Format imprimable"
                            )
                        except Exception as e:
                            st.button(
                                "📑 PDF non disponible",
                                disabled=True,
                                help="Installez kaleido: pip install kaleido"
                            )
    
    else:
        # Message d'accueil si pas de données
        st.info("👈 Commencez par charger vos données dans la barre latérale")
        
        # Exemples d'utilisation
        st.header("💡 Comment utiliser cette application ?")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📁 Option 1 : Fichier CSV")
            st.markdown("""
            1. Sélectionnez "📁 Fichier CSV" dans la barre latérale
            2. Uploadez votre fichier CSV
            3. Configurez votre graphique
            4. Cliquez sur "Générer"
            """)
        
        with col2:
            st.subheader("🌐 Option 2 : API REST")
            st.markdown("""
            1. Sélectionnez "🌐 API REST" dans la barre latérale
            2. Entrez l'URL de votre API
            3. Configurez l'authentification si nécessaire
            4. Cliquez sur "Charger les données"
            """)
        
        # Exemples d'API
        with st.expander("🔗 Exemples d'API publiques pour tester"):
            st.markdown("""
            **APIs publiques sans authentification :**
            - JSONPlaceholder : `https://jsonplaceholder.typicode.com/users`
            - OpenBrewery : `https://api.openbrewerydb.org/breweries`
            - CoinGecko : `https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&per_page=100`
            - COVID-19 : `https://disease.sh/v3/covid-19/countries`
            
            **Format attendu :**
            - JSON : Liste de dictionnaires ou objet avec une clé 'data'/'results'
            - CSV : Format tabulaire standard
            """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Générateur de Graphiques Plotly | "
        "Propulsé par Streamlit & Plotly"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
