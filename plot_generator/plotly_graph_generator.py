import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, Union


def generer_graphique_plotly(
    df: pd.DataFrame,
    type_graphique: str,
    x: str,
    y: Optional[str] = None,
    z: Optional[str] = None,
    titre: Optional[str] = None,
    **kwargs
) -> Union[go.Figure, None]:
    """
    Génère un graphique Plotly selon le type spécifié.
    
    Paramètres:
    -----------
    df : pd.DataFrame
        Le DataFrame contenant les données
    type_graphique : str
        Le type de graphique Plotly parmi:
        - 'scatter' : nuage de points (nécessite x et y)
        - 'line' : graphique en ligne (nécessite x et y)
        - 'bar' : diagramme en barres (nécessite x, y optionnel)
        - 'histogram' : histogramme (nécessite x uniquement)
        - 'box' : boîte à moustaches (nécessite x ou y)
        - 'violin' : graphique en violon (nécessite x ou y)
        - 'pie' : diagramme circulaire (nécessite x pour noms, y pour valeurs)
        - 'sunburst' : diagramme en rayon de soleil (nécessite x)
        - 'treemap' : carte arborescente (nécessite x)
        - 'scatter_3d' : nuage de points 3D (nécessite x, y, z)
        - 'density_heatmap' : carte de densité (nécessite x et y)
        - 'density_contour' : contour de densité (nécessite x et y)
        - 'area' : graphique en aire (nécessite x et y)
    x : str
        Nom de la colonne pour l'axe des abscisses
    y : Optional[str]
        Nom de la colonne pour l'axe des ordonnées (facultatif selon le type)
    z : Optional[str]
        Nom de la colonne pour le facet/segmentation (facultatif)
    titre : Optional[str]
        Titre du graphique (facultatif)
    **kwargs : dict
        Arguments supplémentaires pour personnaliser le graphique
        (ex: color, size, hover_data, etc.)
    
    Returns:
    --------
    go.Figure ou None
        Le graphique Plotly ou None en cas d'erreur
    
    Exemples:
    ---------
    >>> fig = generer_graphique_plotly(df, 'scatter', x='surface_habitable_logement', 
    ...                                 y='conso_totale_mwh', z='etiquette_dpe')
    >>> fig = generer_graphique_plotly(df, 'histogram', x='conso_m2')
    >>> fig = generer_graphique_plotly(df, 'bar', x='etiquette_dpe', y='conso_totale_mwh')
    """
    
    # Liste des types de graphiques supportés
    types_valides = {
        'scatter', 'line', 'bar', 'histogram', 'box', 'violin', 
        'pie', 'sunburst', 'treemap', 'scatter_3d', 
        'density_heatmap', 'density_contour', 'area'
    }
    
    # Validation du type de graphique
    if type_graphique not in types_valides:
        print(f"❌ Erreur: Type de graphique '{type_graphique}' non supporté.")
        print(f"Types valides: {', '.join(sorted(types_valides))}")
        return None
    
    # Validation du DataFrame
    if df is None or df.empty:
        print("❌ Erreur: Le DataFrame est vide ou None.")
        return None
    
    # Validation de la colonne x
    if x not in df.columns:
        print(f"❌ Erreur: La colonne '{x}' n'existe pas dans le DataFrame.")
        print(f"Colonnes disponibles: {', '.join(df.columns.tolist())}")
        return None
    
    # Validation de la colonne y si fournie
    if y is not None and y not in df.columns:
        print(f"❌ Erreur: La colonne '{y}' n'existe pas dans le DataFrame.")
        print(f"Colonnes disponibles: {', '.join(df.columns.tolist())}")
        return None
    
    # Validation de la colonne z si fournie
    if z is not None and z not in df.columns:
        print(f"❌ Erreur: La colonne '{z}' n'existe pas dans le DataFrame.")
        print(f"Colonnes disponibles: {', '.join(df.columns.tolist())}")
        return None
    
    # Configuration du facet si z est fourni
    facet_col = z if z is not None else kwargs.get('facet_col', None)
    if 'facet_col' in kwargs and z is not None:
        kwargs['facet_col'] = z
    elif z is not None:
        kwargs['facet_col'] = z
    
    # Génération du titre par défaut
    if titre is None:
        if y is not None:
            titre = f"{type_graphique.capitalize()}: {y} en fonction de {x}"
        else:
            titre = f"{type_graphique.capitalize()}: {x}"
        if z is not None:
            titre += f" (segmenté par {z})"
    
    try:
        fig = None
        
        # Graphiques nécessitant x et y
        if type_graphique == 'scatter':
            if y is None:
                print("❌ Erreur: Le graphique 'scatter' nécessite les colonnes x et y.")
                return None
            fig = px.scatter(df, x=x, y=y, title=titre, **kwargs)
        
        elif type_graphique == 'line':
            if y is None:
                print("❌ Erreur: Le graphique 'line' nécessite les colonnes x et y.")
                return None
            fig = px.line(df, x=x, y=y, title=titre, **kwargs)
        
        elif type_graphique == 'area':
            if y is None:
                print("❌ Erreur: Le graphique 'area' nécessite les colonnes x et y.")
                return None
            fig = px.area(df, x=x, y=y, title=titre, **kwargs)
        
        elif type_graphique == 'density_heatmap':
            if y is None:
                print("❌ Erreur: Le graphique 'density_heatmap' nécessite les colonnes x et y.")
                return None
            fig = px.density_heatmap(df, x=x, y=y, title=titre, **kwargs)
        
        elif type_graphique == 'density_contour':
            if y is None:
                print("❌ Erreur: Le graphique 'density_contour' nécessite les colonnes x et y.")
                return None
            fig = px.density_contour(df, x=x, y=y, title=titre, **kwargs)
        
        # Graphiques 3D
        elif type_graphique == 'scatter_3d':
            if y is None or z is None:
                print("❌ Erreur: Le graphique 'scatter_3d' nécessite les colonnes x, y et z.")
                return None
            # Pour 3D, z est utilisé comme axe, pas comme facet
            kwargs_3d = {k: v for k, v in kwargs.items() if k != 'facet_col'}
            fig = px.scatter_3d(df, x=x, y=y, z=z, title=titre, **kwargs_3d)
        
        # Graphiques avec x et y optionnel
        elif type_graphique == 'bar':
            if y is not None:
                fig = px.bar(df, x=x, y=y, title=titre, **kwargs)
            else:
                # Si y n'est pas fourni, on compte les occurrences de x
                value_counts = df[x].value_counts().reset_index()
                value_counts.columns = [x, 'count']
                fig = px.bar(value_counts, 
                           x=x, y='count', title=titre, 
                           labels={'count': 'Nombre'}, **kwargs)
        
        # Graphiques nécessitant uniquement x
        elif type_graphique == 'histogram':
            fig = px.histogram(df, x=x, title=titre, **kwargs)
        
        elif type_graphique == 'box':
            if y is not None:
                fig = px.box(df, x=x, y=y, title=titre, **kwargs)
            else:
                fig = px.box(df, y=x, title=titre, **kwargs)
        
        elif type_graphique == 'violin':
            if y is not None:
                fig = px.violin(df, x=x, y=y, title=titre, **kwargs)
            else:
                fig = px.violin(df, y=x, title=titre, **kwargs)
        
        elif type_graphique == 'pie':
            if y is not None:
                fig = px.pie(df, names=x, values=y, title=titre, **kwargs)
            else:
                # Si y n'est pas fourni, on compte les occurrences de x
                value_counts = df[x].value_counts().reset_index()
                value_counts.columns = [x, 'count']
                fig = px.pie(value_counts, names=x, values='count', 
                           title=titre, **kwargs)
        
        elif type_graphique == 'sunburst':
            # Sunburst nécessite une structure hiérarchique
            if y is not None:
                fig = px.sunburst(df, path=[x], values=y, title=titre, **kwargs)
            else:
                print("ℹ️  Info: Pour un sunburst optimal, fournissez y pour les valeurs.")
                fig = px.sunburst(df, path=[x], title=titre, **kwargs)
        
        elif type_graphique == 'treemap':
            # Treemap nécessite une structure hiérarchique
            if y is not None:
                fig = px.treemap(df, path=[x], values=y, title=titre, **kwargs)
            else:
                print("ℹ️  Info: Pour un treemap optimal, fournissez y pour les valeurs.")
                value_counts = df[x].value_counts().reset_index()
                value_counts.columns = [x, 'count']
                fig = px.treemap(value_counts, path=[x], values='count', 
                               title=titre, **kwargs)
        
        # Mise en page améliorée
        if fig is not None:
            fig.update_layout(
                template='plotly_white',
                font=dict(size=12),
                title_font=dict(size=16, family='Arial Black'),
                hoverlabel=dict(bgcolor="white", font_size=12)
            )
            
            print(f"✅ Graphique '{type_graphique}' créé avec succès!")
            return fig
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du graphique: {str(e)}")
        return None


# Fonction utilitaire pour lister les colonnes du DataFrame
def afficher_colonnes(df: pd.DataFrame) -> None:
    """Affiche les colonnes disponibles dans le DataFrame avec leur type."""
    print("\n📊 Colonnes disponibles dans le DataFrame:")
    print("-" * 60)
    for col in df.columns:
        dtype = df[col].dtype
        print(f"  • {col:<40} ({dtype})")
    print("-" * 60)


# Exemple d'utilisation
if __name__ == "__main__":
    # Charger le CSV
    df = pd.read_csv('/mnt/user-data/uploads/1761670645250_pasted-content-1761670645250.txt')
    
    print("=" * 70)
    print("🎨 GÉNÉRATEUR DE GRAPHIQUES PLOTLY")
    print("=" * 70)
    
    # Afficher les colonnes disponibles
    afficher_colonnes(df)
    
    print("\n" + "=" * 70)
    print("📈 EXEMPLES DE GRAPHIQUES")
    print("=" * 70)
    
    # Exemple 1: Scatter plot avec facet
    print("\n1️⃣  Scatter: Consommation vs Surface (par DPE)")
    fig1 = generer_graphique_plotly(
        df, 
        'scatter', 
        x='surface_habitable_logement', 
        y='conso_totale_mwh',
        z='etiquette_dpe',
        color='etiquette_dpe'
    )
    if fig1:
        fig1.show()
    
    # Exemple 2: Histogram avec une seule colonne
    print("\n2️⃣  Histogramme: Distribution des consommations")
    fig2 = generer_graphique_plotly(
        df, 
        'histogram', 
        x='conso_m2',
        color='etiquette_dpe'
    )
    if fig2:
        fig2.show()
    
    # Exemple 3: Bar chart
    print("\n3️⃣  Diagramme en barres: Consommation moyenne par type d'énergie")
    fig3 = generer_graphique_plotly(
        df, 
        'bar', 
        x='type_energie_principale_chauffage',
        y='conso_totale_mwh',
        color='etiquette_dpe'
    )
    if fig3:
        fig3.show()
    
    # Exemple 4: Box plot
    print("\n4️⃣  Box plot: Distribution des coûts par étiquette DPE")
    fig4 = generer_graphique_plotly(
        df, 
        'box', 
        x='etiquette_dpe',
        y='cout_m2'
    )
    if fig4:
        fig4.show()
    
    print("\n" + "=" * 70)
    print("✨ Exemples terminés!")
    print("=" * 70)
