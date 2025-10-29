# DPE Rhône 69 — Analyse & Prédiction Énergétique

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/Scikit--Learn-ML-F7931E?logo=scikit-learn&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-Containerization-2496ED?logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/HuggingFace-Deployment-FFD21E?logo=huggingface&logoColor=black" />
</p>

---

## Présentation du projet

L’application **DPE Rhône 69** combine données publiques et intelligence artificielle pour démocratiser l'accès à l'information énergétique dans le département du Rhône à partir des données ouvertes **ADEME** et **Enedis**.

###  Déploiement en ligne
| Service | Lien direct |
|----------|-------------|
|  **API FastAPI** | [https://riadshrn-api-dpe-conso.hf.space/docs](https://riadshrn-api-dpe-conso.hf.space/docs) |
|  **Application Streamlit** | [https://riadshrn-streamlit-dpe-app.hf.space/](https://riadshrn-streamlit-dpe-app.hf.space/) |

---

##  Objectifs principaux

-  **Analyser** les consommations et émissions énergétiques par commune  
-  **Prédire** automatiquement l’étiquette DPE à partir des caractéristiques d’un logement  
-  **Estimer** la consommation énergétique (kWh/m²/an et MWh/an)  
-  **Interpréter** les résultats à l’aide d’un modèle de langage (Mistral AI)  
-  **Visualiser** les données sur une carte interactive  
-  **Comparer** les moyennes locales par commune  

---

##  Architecture du projet

```
m2_enedis_dpe_app/
│
├── app/                      → API FastAPI (backend)
├── streamlit_app/            → Interface Streamlit (frontend)│
├── data/                     → Données locales (ADEME, Enedis)
├── models/                   → Dossiers de modèles complets
├── notebooks/                → Analyses exploratoires & modélisation
├── docker-compose.yml        → Orchestration multi-conteneurs
└── academic_report/          → Rapport d’étude 
```

---

## Schéma général de l’écosystème applicatif

```mermaid
flowchart TD

    subgraph DATA["Données externes"]
        A1["ADEME API"] --> A
        A2["ENEDIS API"] --> A
        A["Données sources (ADEME / Enedis)"]
    end

    subgraph NOTEBOOK["Traitement & Modélisation"]
        B1["Nettoyage & Fusion des données"]
        B2["EDA (Analyse exploratoire)"]
        B3["Modélisation Machine Learning"]
        B4["3 modèles : 
              • Prédiction conso
              • DPE sans conso
              • DPE avec conso"]
        B1 --> B2 --> B3 --> B4
    end

    subgraph HF_MODELS["Déploiement modèles & données"]
        M1["Modèles ML hébergés sur Hugging Face"]
        M2["Jeu de données fusionné hébergé sur Hugging Face"]
    end

    subgraph API["API FastAPI (Backend)"]
        F1["Endpoints /predict, /interpretation, /data_viz"]
        F2["Appels aux modèles (Hugging Face)"]
        F3["Intégration Mistral AI (LLM interprétation)"]
        F1 --> F2 --> F3
    end

    subgraph APP["Interface Streamlit (Frontend)"]
        S1["Visualisation (Plotly / Mapbox)"]
        S2["Prédiction interactive via API"]
        S3["Export CSV / PNG"]
        S4["Affichage interprétation Mistral"]
        S1 --> S2 --> S3 --> S4
    end

    subgraph USER["Utilisateur"]
        U1["Exploration & Prédiction"]
    end

    %% Relations entre blocs
    A --> NOTEBOOK
    NOTEBOOK --> HF_MODELS
    HF_MODELS --> API
    USER --> APP
    API --> APP
    APP --> API
    APP --> USER
    

```

---

##  Fonctionnalités principales

| Catégorie | Fonctionnalité |
|------------|----------------|
|  **Visualisation** | Carte interactive des logements du Rhône avec couleurs par étiquette DPE |
|  **Dashboard DPE** | Analyse de la distribution énergétique et des émissions GES |
|  **Prédiction IA** | Estimation de la classe énergétique et de la consommation annuelle |
|  **Interprétation automatique** | Conseils générés par Mistral AI |
|  **Exports** | Téléchargement des données filtrées (CSV) et graphiques (PNG) |
|  **API REST** | Endpoints pour prédiction, données et métadonnées |
|  **Docker** | Conteneurisation et déploiement multi-service |

---

##  Technologies utilisées

| Domaine | Outil | Description |
|----------|--------|-------------|
| **Backend** | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white) | Framework web Python asynchrone |
| **Frontend** | ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white) | Interface interactive et dynamique |
| **Machine Learning** | ![Scikit-learn](https://img.shields.io/badge/Scikit--Learn-F7931E?logo=scikit-learn&logoColor=white) | Entraînement et prédiction des modèles |
| **Visualisation** | ![Plotly](https://img.shields.io/badge/Plotly-2391E6?logo=plotly&logoColor=white) | Graphiques et cartes Mapbox |
| **Conteneurisation** | ![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white) | Déploiement et portabilité |
| **IA Générative** | ![Mistral AI](https://img.shields.io/badge/Mistral%20AI-FFD21E?logo=huggingface&logoColor=black) | Génération automatique de conseils |
| **Déploiement Cloud** | ![Hugging Face](https://img.shields.io/badge/HuggingFace-FFD21E?logo=huggingface&logoColor=black) | Hébergement API + App |
| **Data** | ![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white) | Traitement et préparation des données |
| **Stockage** | ![Parquet](https://img.shields.io/badge/Parquet-4B8BBE?logo=apache&logoColor=white) | Données compressées efficaces |

---

##  Déploiement local avec Docker

### Prérequis
- **Docker Desktop** installé  
- (Optionnel) **Python 3.10+** si exécution manuelle

### Étapes
```bash
# Construction et démarrage
docker compose up --build

# Arrêt des services
docker compose down
```

### Accès local
| Service | URL | Description |
|----------|-----|-------------|
|  Streamlit | http://localhost:8501 | Interface principale |
|  FastAPI | http://localhost:8000 | Backend et API |
|  Swagger | http://localhost:8000/docs | Documentation interactive |

---

##  Exécution sans Docker

**Backend :**
```bash
cd app
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend :**
```bash
cd streamlit_app
pip install -r requirements.txt
streamlit run app.py
```

---

##  Exemples d’endpoints API

| Méthode | Endpoint | 
|----------|-----------|
| `GET /` | Accueil |
| `POST /predict_dpe_sans_conso` | Prédiction étiquette DPE sans conso |
| `POST /predict_dpe_avec_conso` | Prédiction DPE avec conso |
| `POST /predict_conso` | Estimation consommation |
| `POST /interpretation` | Analyse Mistral AI |
| `GET /metadata` | Données de l'adem et enedis |
| `GET /data_viz` | Données agrégées pour visualisation |


---

## Ressources associées
- [Documentation technique](./academic_report/DOCUMENTATION_TECHNIQUE.md)
- [Rapport académique (Markdown)](./academic_report/)
- [Notebooks de modélisation](./notebooks/)
- [Docker Compose](./docker-compose.yml)
