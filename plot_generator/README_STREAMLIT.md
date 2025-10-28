# 🚀 Application Streamlit - Générateur de Graphiques Plotly

## 📋 Description

Application web interactive permettant de créer des visualisations Plotly à partir de :
- **Fichiers CSV** uploadés
- **APIs REST** (avec ou sans authentification)

Interface utilisateur complète avec listes déroulantes pour sélectionner :
- Type de graphique
- Colonnes X, Y, Z
- Options de personnalisation

---

## ⚡ Installation rapide

### 1. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 2. Lancer l'application

```bash
streamlit run app_streamlit.py
```

L'application s'ouvrira automatiquement dans votre navigateur à l'adresse :
`http://localhost:8501`

---

## 📦 Structure des fichiers

```
.
├── app_streamlit.py          # Application principale
├── plotly_graph_generator.py # Module de génération
├── requirements.txt          # Dépendances Python
└── README_STREAMLIT.md       # Ce fichier
```

---

## 🎯 Fonctionnalités

### 📁 Chargement CSV
- Upload de fichiers CSV via l'interface
- Aperçu des données
- Informations sur les colonnes

### 🌐 Chargement API
- **URL personnalisée** : Connectez-vous à n'importe quelle API REST
- **Authentification** :
  - Bearer Token
  - API Key
  - Custom Header
- **Paramètres de requête** : Ajoutez des paramètres GET
- **Formats supportés** : JSON, CSV

### 🎨 Configuration du graphique
- **13 types de graphiques** disponibles
- **Listes déroulantes** pour :
  - Sélection des colonnes X, Y, Z
  - Type de graphique
  - Couleur, taille, hover data
- **Titre personnalisé**
- **Options avancées** : color, size, hover_data

### 💾 Export
- **HTML** : Format interactif (toujours disponible)
- **PNG** : Image haute qualité (si kaleido installé)
- **PDF** : Format imprimable (si kaleido installé)

---

## 📊 Utilisation

### Option 1 : Fichier CSV

1. Dans la barre latérale, sélectionnez **"📁 Fichier CSV"**
2. Cliquez sur **"Browse files"** et uploadez votre CSV
3. Visualisez vos données dans l'aperçu
4. Configurez votre graphique :
   - Choisissez le type de graphique
   - Sélectionnez la colonne X (obligatoire)
   - Sélectionnez Y et Z si nécessaire
   - Personnalisez avec couleur, taille, etc.
5. Cliquez sur **"🚀 Générer le graphique"**
6. Téléchargez en HTML, PNG ou PDF

### Option 2 : API REST

1. Dans la barre latérale, sélectionnez **"🌐 API REST"**
2. Entrez l'**URL de votre API**
3. **(Optionnel)** Configurez l'authentification :
   - Cliquez sur "🔧 Options avancées"
   - Cochez "Authentification"
   - Choisissez le type (Bearer Token, API Key, Custom)
   - Entrez vos identifiants
4. **(Optionnel)** Ajoutez des paramètres de requête
5. Cliquez sur **"🔄 Charger les données"**
6. Suivez les mêmes étapes que pour le CSV

---

## 🔗 Exemples d'API

### APIs publiques (sans authentification)

#### 1. JSONPlaceholder (Utilisateurs)
```
URL: https://jsonplaceholder.typicode.com/users
Format: JSON (liste)
Colonnes: id, name, username, email, address, company
```

#### 2. OpenBrewery (Brasseries)
```
URL: https://api.openbrewerydb.org/breweries
Format: JSON (liste)
Colonnes: name, brewery_type, city, state, country
```

#### 3. CoinGecko (Cryptomonnaies)
```
URL: https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&per_page=100
Format: JSON (liste)
Colonnes: name, current_price, market_cap, price_change_percentage_24h
```

#### 4. COVID-19 (Données par pays)
```
URL: https://disease.sh/v3/covid-19/countries
Format: JSON (liste)
Colonnes: country, cases, deaths, recovered, active
```

### Votre API (avec authentification)

#### Format attendu de l'API

**Option 1 : Liste de dictionnaires**
```json
[
  {"colonne1": "valeur1", "colonne2": 123, "colonne3": "A"},
  {"colonne1": "valeur2", "colonne2": 456, "colonne3": "B"}
]
```

**Option 2 : Objet avec clé 'data'/'results'**
```json
{
  "data": [
    {"colonne1": "valeur1", "colonne2": 123},
    {"colonne1": "valeur2", "colonne2": 456}
  ],
  "total": 2
}
```

**Option 3 : CSV**
```
colonne1,colonne2,colonne3
valeur1,123,A
valeur2,456,B
```

#### Exemple avec authentification Bearer Token

1. URL : `https://votre-api.com/data`
2. Cochez "Authentification"
3. Sélectionnez "Bearer Token"
4. Entrez votre token : `votre_token_secret`
5. Cliquez "Charger les données"

#### Exemple avec API Key

1. URL : `https://votre-api.com/data`
2. Cochez "Authentification"
3. Sélectionnez "API Key"
4. API Key : `votre_api_key`
5. Nom de la clé : `X-API-Key` (ou autre selon votre API)
6. Cliquez "Charger les données"

---

## 🎨 Types de graphiques disponibles

| Type | Description | Colonnes requises |
|------|-------------|-------------------|
| `scatter` | Nuage de points | x, y |
| `line` | Graphique en ligne | x, y |
| `bar` | Diagramme en barres | x |
| `histogram` | Histogramme | x |
| `box` | Boîte à moustaches | x ou y |
| `violin` | Graphique en violon | x ou y |
| `pie` | Diagramme circulaire | x |
| `sunburst` | Diagramme soleil | x |
| `treemap` | Carte arborescente | x |
| `scatter_3d` | Nuage 3D | x, y, z |
| `density_heatmap` | Carte de densité | x, y |
| `density_contour` | Contour de densité | x, y |
| `area` | Graphique en aire | x, y |

---

## 💡 Conseils d'utilisation

### Sélection des colonnes

**Colonne X (obligatoire)**
- Toujours requise
- Axe des abscisses

**Colonne Y (optionnelle)**
- Nécessaire pour : scatter, line, area, density_heatmap, density_contour
- Optionnelle pour : bar, box, violin, pie

**Colonne Z (optionnelle)**
- Pour le **faceting** : crée des sous-graphiques par catégorie
- Pour **scatter_3d** : utilisée comme 3ème dimension

### Options de personnalisation

**Couleur par**
- Colore les points selon une variable catégorielle
- Crée automatiquement une légende

**Taille des points par**
- Varie la taille selon une variable numérique
- Utile pour scatter plots

**Infos au survol**
- Sélectionnez plusieurs colonnes
- Affichées au survol de la souris

---

## 🔧 Configuration avancée

### Modifier le port de l'application

```bash
streamlit run app_streamlit.py --server.port 8502
```

### Désactiver l'ouverture automatique du navigateur

```bash
streamlit run app_streamlit.py --server.headless true
```

### Modifier le thème

Créez un fichier `.streamlit/config.toml` :

```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

---

## 📝 Exemples de cas d'usage

### Cas 1 : Analyse de données énergétiques (CSV)

```
Fichier : donnees_energetiques.csv
Type de graphique : scatter
X : surface_habitable_logement
Y : conso_totale_mwh
Z : type_batiment (faceting)
Couleur : etiquette_dpe
```

### Cas 2 : Tracking crypto en temps réel (API)

```
URL : https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&per_page=100
Type de graphique : scatter
X : market_cap
Y : current_price
Couleur : name
Taille : total_volume
```

### Cas 3 : Comparaison de données COVID (API)

```
URL : https://disease.sh/v3/covid-19/countries
Type de graphique : bar
X : country
Y : cases
Couleur : continent
```

---

## 🐛 Dépannage

### Erreur : "No module named 'streamlit'"

**Solution :**
```bash
pip install streamlit
```

### Erreur : "No module named 'plotly_graph_generator'"

**Solution :**
Assurez-vous que `plotly_graph_generator.py` est dans le même dossier que `app_streamlit.py`

### PNG/PDF non disponible

**Solution :**
```bash
pip install kaleido
```

### Erreur de connexion à l'API

**Vérifications :**
1. L'URL est correcte
2. L'API est accessible (testez dans le navigateur)
3. L'authentification est correcte
4. Les paramètres sont valides

### L'application ne se charge pas

**Solutions :**
1. Vérifiez que streamlit est installé
2. Vérifiez que le port 8501 n'est pas déjà utilisé
3. Essayez un autre port : `streamlit run app_streamlit.py --server.port 8502`

---

## 🚀 Déploiement

### Streamlit Cloud (gratuit)

1. Créez un compte sur [streamlit.io](https://streamlit.io/cloud)
2. Connectez votre dépôt GitHub
3. Sélectionnez `app_streamlit.py` comme fichier principal
4. Déployez !

### Heroku

```bash
# Créer Procfile
echo "web: streamlit run app_streamlit.py --server.port $PORT" > Procfile

# Déployer
heroku create
git push heroku main
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app_streamlit.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

## 📚 Ressources

- [Documentation Streamlit](https://docs.streamlit.io/)
- [Documentation Plotly](https://plotly.com/python/)
- [API REST Tutorial](https://restfulapi.net/)

---

## 🎯 Roadmap / Améliorations futures

- [ ] Support d'autres sources de données (SQL, MongoDB)
- [ ] Sauvegarde des configurations
- [ ] Historique des graphiques
- [ ] Templates de graphiques
- [ ] Export vers Excel
- [ ] Mode dark/light
- [ ] Annotations sur les graphiques
- [ ] Filtres interactifs sur les données

---

## 💬 Support

Pour toute question ou problème :
1. Consultez d'abord ce README
2. Vérifiez les exemples fournis
3. Testez avec une API publique pour isoler le problème

---

**Créé avec ❤️ | Propulsé par Streamlit & Plotly**
