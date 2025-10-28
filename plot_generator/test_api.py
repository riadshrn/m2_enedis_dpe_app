"""
Exemple de script pour tester le chargement de données depuis une API
et la génération de graphiques
"""

import pandas as pd
import requests
from plotly_graph_generator import generer_graphique_plotly


def charger_api_exemple(url):
    """Charge des données depuis une API et retourne un DataFrame."""
    try:
        print(f"📡 Chargement depuis : {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Si c'est une liste de dictionnaires
        if isinstance(data, list):
            df = pd.DataFrame(data)
        # Si c'est un dict avec une clé 'data'/'results'
        elif isinstance(data, dict):
            for key in ['data', 'results', 'items', 'records']:
                if key in data:
                    df = pd.DataFrame(data[key])
                    break
            else:
                df = pd.DataFrame([data])
        
        print(f"✅ {len(df)} lignes chargées")
        return df
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None


def exemple_jsonplaceholder():
    """Exemple avec l'API JSONPlaceholder (utilisateurs)."""
    print("\n" + "=" * 70)
    print("EXEMPLE 1: JSONPlaceholder - Utilisateurs")
    print("=" * 70)
    
    url = "https://jsonplaceholder.typicode.com/users"
    df = charger_api_exemple(url)
    
    if df is not None:
        print(f"\nColonnes disponibles : {', '.join(df.columns)}")
        
        # Graphique scatter des coordonnées géographiques
        fig = generer_graphique_plotly(
            df,
            'scatter',
            x='id',
            y='name',
            titre="Utilisateurs JSONPlaceholder"
        )
        
        if fig:
            fig.write_html('/mnt/user-data/outputs/api_exemple1_jsonplaceholder.html')
            print("💾 Graphique sauvegardé: api_exemple1_jsonplaceholder.html")


def exemple_coingecko():
    """Exemple avec l'API CoinGecko (cryptomonnaies)."""
    print("\n" + "=" * 70)
    print("EXEMPLE 2: CoinGecko - Top 50 Cryptomonnaies")
    print("=" * 70)
    
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&per_page=50"
    df = charger_api_exemple(url)
    
    if df is not None:
        print(f"\nColonnes disponibles : {', '.join(df.columns)}")
        print(f"\nAperçu :")
        print(df[['name', 'current_price', 'market_cap']].head())
        
        # Graphique scatter market cap vs price
        fig = generer_graphique_plotly(
            df,
            'scatter',
            x='market_cap',
            y='current_price',
            titre="Cryptomonnaies : Market Cap vs Prix",
            color='name',
            hover_data=['name', 'symbol']
        )
        
        if fig:
            fig.write_html('/mnt/user-data/outputs/api_exemple2_crypto.html')
            print("💾 Graphique sauvegardé: api_exemple2_crypto.html")


def exemple_covid():
    """Exemple avec l'API COVID-19."""
    print("\n" + "=" * 70)
    print("EXEMPLE 3: COVID-19 - Données par pays")
    print("=" * 70)
    
    url = "https://disease.sh/v3/covid-19/countries"
    df = charger_api_exemple(url)
    
    if df is not None:
        print(f"\nColonnes disponibles : {', '.join(df.columns)}")
        
        # Top 20 pays par nombre de cas
        df_top20 = df.nlargest(20, 'cases')
        
        # Graphique bar
        fig = generer_graphique_plotly(
            df_top20,
            'bar',
            x='country',
            y='cases',
            titre="COVID-19 : Top 20 pays par nombre de cas",
            color='continent'
        )
        
        if fig:
            fig.write_html('/mnt/user-data/outputs/api_exemple3_covid.html')
            print("💾 Graphique sauvegardé: api_exemple3_covid.html")


def exemple_breweries():
    """Exemple avec l'API OpenBrewery."""
    print("\n" + "=" * 70)
    print("EXEMPLE 4: OpenBrewery - Brasseries USA")
    print("=" * 70)
    
    url = "https://api.openbrewerydb.org/breweries?per_page=100"
    df = charger_api_exemple(url)
    
    if df is not None:
        print(f"\nColonnes disponibles : {', '.join(df.columns)}")
        
        # Distribution par type
        fig = generer_graphique_plotly(
            df,
            'pie',
            x='brewery_type',
            titre="Distribution des brasseries par type"
        )
        
        if fig:
            fig.write_html('/mnt/user-data/outputs/api_exemple4_breweries.html')
            print("💾 Graphique sauvegardé: api_exemple4_breweries.html")


def main():
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                                                                ║")
    print("║      🌐 EXEMPLES DE CHARGEMENT DEPUIS DES APIs REST           ║")
    print("║                                                                ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    
    print("\n📌 Ce script teste le chargement de données depuis différentes APIs")
    print("📌 et génère des graphiques automatiquement\n")
    
    # Exécuter les exemples
    exemple_jsonplaceholder()
    exemple_coingecko()
    exemple_covid()
    exemple_breweries()
    
    print("\n" + "=" * 70)
    print("✨ TOUS LES EXEMPLES TERMINÉS")
    print("=" * 70)
    print("\n📁 4 graphiques HTML générés dans le dossier outputs/")
    print("💡 Ouvrez-les dans un navigateur pour les visualiser !\n")


if __name__ == "__main__":
    main()
