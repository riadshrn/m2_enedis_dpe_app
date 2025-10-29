# Documentation Technique — Application DPE Rhône 69

## Objectif

L’application **DPE Rhône 69** permet d’analyser et de prédire la **performance énergétique (étiquette DPE)** et la **consommation annuelle** des logements du département du Rhône à partir des données publiques **ADEME** et **Enedis**.

Elle repose sur trois modules principaux :
1. Une **API FastAPI** pour la prédiction et l’interprétation IA.  
2. Une **interface Streamlit** pour la visualisation et l’interaction utilisateur.  
3. Une **infrastructure Docker** pour le déploiement reproductible et simplifié.

---

## Architecture du système

### Schéma d’architecture général

<p align="center">
  <img src="../img/Architecture.png" alt="Schéma général de l'application DPE Rhône 69" width="700">
</p>

Ce schéma illustre le flux de traitement complet :  
- **Récupération des données ADEME et Enedis via leurs APIs publiques**  
- **Nettoyage, fusion et analyse exploratoire (EDA) dans les notebooks**  
- **Modélisation Machine Learning** : trois modèles (consommation, DPE sans conso, DPE avec conso)  
- **Déploiement sur Hugging Face** des modèles, de l’API FastAPI et de l’application Streamlit  
- **Intégration Mistral AI** pour l’interprétation des résultats

---

## Installation sur poste local (via Docker)

### Prérequis
- **Docker Desktop** installé (version ≥ 24.0)
- Connexion internet active
- (Optionnel) **Python ≥ 3.10** si exécution manuelle sans Docker

---

### Clonage du dépôt

```bash
git clone https://github.com/riadshrn/m2_enedis_dpe_app.git
cd m2_enedis_dpe_app
```

---

### Lancement complet avec Docker Compose

```bash
docker compose up --build
```
 Premier lancement : environ **1 à 2 minutes** pour la construction des images.

---

###  Accès aux services

| Service | URL locale | Description |
|----------|-------------|--------------|
| **Streamlit App** | http://localhost:8501 | Interface utilisateur |
| **FastAPI** | http://localhost:8000 | API de prédiction |
| **Swagger UI** | http://localhost:8000/docs | Documentation API |

---

### Arrêt et maintenance

```bash
docker compose down
```

Pour relancer uniquement l’API :
```bash
docker compose up api
```

---

## Environnement logiciel et bibliothèques

### Backend – API (FastAPI)

| Package | Version actuelle (2025) | Description |
|----------|--------------------------|-------------|
| `fastapi` | 0.115.4 | Framework web Python asynchrone |
| `uvicorn` | 0.32.0 | Serveur ASGI pour FastAPI |
| `pandas` | 2.2.3 | Manipulation de données |
| `scikit-learn` | 1.5.2 | Modélisation et apprentissage automatique |
| `joblib` | 1.4.2 | Sérialisation des modèles |
| `requests` | 2.32.3 | Requêtes HTTP (API / Mistral) |
| `tqdm` | 4.66.5 | Barre de progression |
| `pyarrow` | 17.0.0 | Format de données Parquet |
| `fastparquet` | 2024.5.0 | Lecture/écriture de fichiers Parquet |

---

### Frontend – Interface Streamlit

| Package | Version actuelle (2025) | Description |
|----------|--------------------------|-------------|
| `streamlit` | 1.38.0 | Interface web interactive |
| `pandas` | 2.2.3 | Manipulation de DataFrame |
| `plotly` | 5.24.1 | Visualisation interactive et cartes Mapbox |
| `requests` | 2.32.3 | Communication avec l’API FastAPI |
| `kaleido` | 0.2.1 | Export d’images Plotly (PNG) |
| `streamlit_plotly_events` | 0.0.6 | Interaction entre graphiques et Streamlit |

---

## Structure du projet

```
m2_enedis_dpe_app/
│
├── app/                → API FastAPI (backend)
├── streamlit_app/      → Application Streamlit (frontend)
├── data/               → Données ADEME & Enedis
├── models/             → Modèles Machine Learning
├── notebooks/          → EDA, nettoyage et modélisation
├── docker-compose.yml  → Orchestration Docker
└── academic_report/    → Documentation & rapport
```

---

## Déploiement Hugging Face

| Composant | URL |
|------------|-----|
|  **API FastAPI** | [https://riadshrn-api-dpe-conso.hf.space/docs](https://riadshrn-api-dpe-conso.hf.space/docs) |
| **App Streamlit** | [https://riadshrn-streamlit-dpe-app.hf.space](https://riadshrn-streamlit-dpe-app.hf.space) |

