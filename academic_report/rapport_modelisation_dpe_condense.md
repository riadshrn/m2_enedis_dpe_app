# Modélisation Prédictive du Diagnostic de Performance Énergétique
## Analyse Comparative Multi-Modèles - Département du Rhône (69)

*Projet Python/ML - M2 SISE - Promotion 2025-2026*  
*Romain BUONO, Mohamed Riad SAHRANE, Abdourahmane TIMERA*

---

## 1. Introduction et Contexte

Le Diagnostic de Performance Énergétique (DPE) constitue un instrument réglementaire majeur dans la politique énergétique française. Ce projet vise à **démocratiser l'accès à l'information énergétique** dans le département du Rhône en développant une application web capable de prédire automatiquement l'étiquette DPE d'un logement.

### 1.1 Originalité de l'Approche

L'étude développe une **architecture modulaire à trois modèles complémentaires** :

1. **Modèle de classification directe** : Prédiction de l'étiquette DPE à partir des caractéristiques physiques du bâtiment
2. **Modèle de régression énergétique** : Estimation de la consommation en kWh/m²/an
3. **Modèle de classification augmentée** : Prédiction DPE intégrant la consommation (renseignée ou prédite)

### 1.2 Données Utilisées

**Base ADEME des DPE** :
- Volume : 358 302 logements (post-nettoyage)
- Périmètre : Département du Rhône (69)
- Variables : 27 features finales (12 numériques, 12 catégorielles, 1 mixte)

**Données Enedis** :
- Consommations électriques réelles agrégées par IRIS
- Enrichissement géospatial des données ADEME

---

## 2. Préparation des Données

### 2.1 Pipeline de Traitement

```
┌─────────────────────────────────────────────────────────────────┐
│                    SOURCES DE DONNÉES                           │
├──────────────────┬──────────────────┬───────────────────────────┤
│  df_adem_69.csv  │ df_adem_neuf.csv │      df_enedis_69.csv     │
│    n=321,548     │    n=36,754      │        n=2,847            │
└────────┬─────────┴────────┬─────────┴──────────┬────────────────┘
         │                  │                    │
         └──────────┬───────┘                    │
                    ↓                            ↓
         ┌──────────────────────┐    ┌──────────────────────┐
         │  FUSION & NETTOYAGE  │    │  NETTOYAGE ENEDIS    │
         └──────────┬───────────┘    └──────────┬───────────┘
                    │                           │
                    └──────────┬────────────────┘
                               ↓
                    ┌──────────────────────────────┐
                    │  JOINTURE SPATIALE (IRIS)    │
                    └──────────┬───────────────────┘
                               ↓
                    ┌──────────────────────────────┐
                    │   FEATURE ENGINEERING        │
                    └──────────┬───────────────────┘
                               ↓
                    ┌──────────────────────────────┐
                    │     DATASET FINAL ML         │
                    │      n=358,302               │
                    └──────────────────────────────┘
```

### 2.2 Nettoyage des Données

**Critères d'exclusion appliqués** :
- Consommation énergétique > 2000 kWh/m²/an (valeurs physiquement impossibles)
- Surface habitable < 9 m² ou > 500 m²
- Année de construction < 1800 ou > 2024

**Résultat** : Exclusion de 2.7% du dataset initial (9 456 observations).

### 2.3 Variables Créées 

**Variables temporelles** :
```python
anciennete = 2024 - annee_construction
classe_annee_construction = ['Avant 1948', '1948-1974', '1975-1989', 
                              '1990-2004', '2005-2011', 'Post-RT2012']
```

**Score composite d'isolation** :
```python
score_isolation_moyen = mean(isolation_toiture, qualite_isolation_murs, 
                             qualite_isolation_menuiseries)
```

**Regroupement énergétique** : 15 modalités → 4 catégories (Électricité, Gaz, Fioul, Autres)

### 2.4 Réduction Dimensionnelle

Variables éliminées par colinéarité (|r| > 0.90) :

| Variable Supprimée          | Variable Conservée      | Corrélation |
|-----------------------------|-------------------------|-------------|
| `emission_ges_5_usages`     | `conso_5_usages_ep`     | 0.93        |
| `cout_total_5_usages`       | `conso_5_usages_ep`     | 0.95        |
| `conso_chauffage_ep`        | `conso_5_usages_ep`     | 0.98        |
| `emission_ges_chauffage`    | `conso_5_usages_ep`     | 0.94        |

### 2.5 Regroupement des Classes DPE

Les 7 classes DPE originales ont été regroupées en **5 classes** pour améliorer la robustesse :

| Classe Regroupée | Étiquettes | Proportion | Effectif   |
|------------------|------------|------------|------------|
| **A_B**          | A, B       | 5.3%       | 18 970     |
| **C**            | C          | 38.5%      | 137 783    |
| **D**            | D          | 31.3%      | 112 058    |
| **E**            | E          | 17.0%      | 60 889     |
| **F_G**          | F, G       | 8.0%       | 28 602     |

**Partitionnement Train/Test** : 80% / 20% avec stratification (286 641 / 71 661 observations)

---

## 3. Comparaison des Algorithmes de Classification

### 3.1 Algorithmes Testés

Quatre algorithmes ont été évalués avec gestion du déséquilibre via **SMOTE** :

| Algorithme                | Hyperparamètres Principaux                                      |
|---------------------------|-----------------------------------------------------------------|
| **Random Forest**         | n_estimators=100, min_samples_split=5, max_features='sqrt'      |
| **Régression Logistique** | max_iter=200, solver='lbfgs', multi_class='multinomial'         |
| **Arbre de Décision**     | criterion='gini', max_depth=None                                |
| **Gradient Boosting**     | n_estimators=100, learning_rate=0.1, max_depth=3                |

### 3.2 Résultats sur Classification 7 Classes

**Performances globales** (ensemble test : 81 037 observations) :

| Modèle                    | Accuracy  | Précision | Rappel | F1-Score | Temps Entraînement |
|---------------------------|-----------|-----------|--------|----------|---------------------|
| **Random Forest**         | **92.12%** | 91.23%   | 83.49% | **86.89%** | 9 min 6 s          |
| Gradient Boosting         | 75.64%    | 76.01%    | 68.23% | 71.84%   | 14 min 32 s         |
| Arbre de Décision         | 89.55%    | 87.12%    | 79.84% | 83.30%   | 47 s                |
| Régression Logistique     | 74.35%    | 79.33%    | 71.56% | 75.12%   | 2 min 18 s          |

**Observations** :
- Random Forest surpasse tous les autres algorithmes avec +26.67 points vs Arbre Simple
- Gradient Boosting sous-performe de façon surprenante (-16.48 points F1 vs Random Forest)

### 3.3 Performances par Classe (Random Forest, 7 Classes)

| Classe | Support | Précision | Rappel | F1-Score | Analyse                                          |
|--------|---------|-----------|--------|----------|--------------------------------------------------|
| **A**  | 205     | 84.2%     | 62.4%  | 71.8%    | Classe très minoritaire (0.25%)                  |
| **B**  | 2 047   | 90.7%     | 71.7%  | 80.1%    | Performance honorable malgré déséquilibre        |
| **C**  | 28 445  | 94.3%     | 95.8%  | 95.0%    | Classe majoritaire : excellente détection        |
| **D**  | 27 114  | 92.1%     | 93.9%  | 93.0%    | Très bonne performance                           |
| **E**  | 15 155  | 91.4%     | 91.3%  | 91.4%    | Équilibre précision-rappel optimal               |
| **F**  | 4 972   | 88.1%     | 81.6%  | 84.7%    | Confusion fréquente avec classe G                |
| **G**  | 3 099   | 94.3%     | 86.8%  | 90.4%    | Classe extrême bien identifiée                   |

### 3.4 Justification du Choix Random Forest



| Critère                      | Poids | Random Forest | Gradient Boosting | Arbre Simple | Régression Logistique |
|------------------------------|-------|---------------|-------------------|--------------|-----------------------|
| **Performance Test (F1)**    | 40%   | 86.89% 🏆    | 71.84%            | 83.30%       | 75.12%                |


\
**Avantages du Random Forest** :  
- Réduction variance par agrégation (100 arbres)  
- Robustesse aux outliers (bootstrap sampling)  
- Gestion implicite des interactions non-linéaires  

---

## 4. Architecture des Trois Modèles Développés

### 4.1 Vue d'Ensemble

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENTRÉES UTILISATEUR                          │
│  Caractéristiques du Logement (surface, année, isolation...)    │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ├──────────────────┬───────────────────┬──────────
                 │                  │                   │
                 ▼                  ▼                   ▼
         ┌───────────────┐  ┌──────────────┐  ┌───────────────────┐
         │   MODÈLE 1    │  │   MODÈLE 2   │  │     MODÈLE 3      │
         │ Classification│  │  Régression  │  │  Classification   │
         │  DPE Directe  │  │ Consommation │  │  DPE Augmentée    │
         │   Input: 24   │  │  Input: 24   │  │  Input: 24 + 1    │
         │   Output: DPE │  │Output: kWh/m²│  │   Output: DPE     │
         └───────┬───────┘  └──────┬───────┘  └─────────┬─────────┘
                 │                 │                    │
                 ▼                 └────────┬───────────┘
         ┌───────────────┐                  ▼
         │ Prédiction DPE│         ┌──────────────────┐
         │ Accuracy 79.0%│         │  Chaîne Complète │
         │  (45 ms)      │         │   DPE via Conso  │
         └───────────────┘         │  Accuracy 67.0%  │
                                   └──────────────────┘
```

### 4.2 Modèle 1 : Classification DPE Directe (Sans Consommation)

**Objectif** : Prédire l'étiquette DPE à partir des caractéristiques physiques uniquement.

**Variables utilisées (24)** :
- **Numériques** : surface_habitable, hauteur_sous_plafond, nombre_niveau, anciennete, score_isolation_moyen, conso_ecs_ep, volume_logement, inertie_lourde
- **Catégorielles** : type_batiment, energie_regroupee, zone_climatique, classe_annee_construction, qualite_isolation_murs, type_installation_chauffage, etc.

**Architecture** :
```python
Pipeline([
    ('preprocess', ColumnTransformer([
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(), categorical_features)
    ])),
    ('smote', SMOTE(random_state=42)),
    ('classifier', RandomForestClassifier(
        n_estimators=100, min_samples_split=5, random_state=42
    ))
])
```

**Performances (5 classes regroupées, test = 71 661 obs)** :

| Métrique              | Valeur   |
|-----------------------|----------|
| **Accuracy**          | **79.0%**|
| **Précision (macro)** | 77.8%    |
| **Rappel (macro)**    | 76.4%    |
| **F1-Score (macro)**  | **76.9%**|

**Performances par classe** :

| Classe DPE | Support | Précision | Rappel | F1-Score |
|------------|---------|-----------|--------|----------|
| **A_B**    | 3 747   | 91.2%     | 94.1%  | **92.6%**|
| **C**      | 27 568  | 86.1%     | 89.8%  | **87.9%**|
| **D**      | 22 412  | 80.5%     | 81.2%  | **80.8%**|
| **E**      | 12 178  | 75.3%     | 71.8%  | **73.5%**|
| **F_G**    | 5 756   | 88.7%     | 79.4%  | **83.8%**|

**Top 10 variables influentes** :

```
1. conso_ecs_ep                    │████████████│ 14.2%
2. anciennete                      │██████████  │ 12.1%
3. volume_logement                 │█████████   │ 10.8%
4. score_isolation_moyen           │████████    │ 9.7%
5. type_energie=ÉLECTRICITÉ        │███████     │ 8.5%
6. classe_annee=1975-1990          │██████      │ 7.2%
7. isolation_toiture=BONNE         │█████       │ 6.1%
8. zone_climatique=H1c             │█████       │ 5.8%
9. hauteur_sous_plafond            │████        │ 5.1%
10. nombre_niveau_logement         │████        │ 4.7%
```

### 4.3 Modèle 2 : Régression de la Consommation Énergétique

**Objectif** : Estimer la consommation en kWh/m²/an pour prédiction en chaîne.

**Transformation logarithmique** :
```python
y_train_log = np.log1p(df_train['conso_m2'])
y_pred = np.expm1(pipeline.predict(X_test))
```

La transformation permet de travailler sur une variable distribuée normalement

**Impact de la transformation** :

| Métrique | Sans log1p | Avec log1p | Gain      |
|----------|------------|------------|-----------|
| **R²**   | 0.821      | **0.872**  | **+6.2%** |
| **RMSE** | 34.7 kWh   | **28.4**   | -18.2%    |
| **MAE**  | 26.3 kWh   | **21.7**   | -17.5%    |

**Architecture** :
```python
Pipeline([
    ('preprocess', ColumnTransformer([
        ('num', Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', RobustScaler())
        ]), numerical_features),
        ('cat', Pipeline([
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ]), categorical_features)
    ])),
    ('feature_selection', SelectKBest(f_regression, k=10)),
    ('regressor', RandomForestRegressor(
        n_estimators=400, max_depth=None, random_state=42, n_jobs=-1
    ))
])
```

**Performances (test = 71 661 logements)** :

| Métrique                          | Valeur                |
|-----------------------------------|-----------------------|
| **Coefficient R²**                | **0.872**             |
| **RMSE**                          | **28.4 kWh/m²/an**    |
| **MAE**                           | **21.7 kWh/m²/an**    |
| **MAPE**                          | **11.2%**             |
| **R² Validation Croisée (5-fold)**| 0.871 ± 0.012         |

### 4.4 Modèle 3 : Classification DPE Augmentée

**Objectif dual** : Intégration de la consommation comme feature additionnelle.

**Mode A : Supervisé (Consommation Renseignée)**
- L'utilisateur fournit sa facture énergétique
- **Accuracy : 99.0%** (quasi-parfaite)

**Mode B : Chaîné (Consommation Prédite)**
- Prédiction en deux étapes : Modèle 2 → Modèle 3
- **Accuracy : 67.0%** (dégradation due à propagation d'erreur)

**Performances Mode Supervisé** :

| Classe DPE | Précision | Rappel | F1-Score |
|------------|-----------|--------|----------|
| **A_B**    | 99.1%     | 99.8%  | 99.4%    |
| **C**      | 99.3%     | 99.7%  | 99.5%    |
| **D**      | 98.9%     | 99.1%  | 99.0%    |
| **E**      | 98.1%     | 97.8%  | 97.9%    |
| **F_G**    | 98.7%     | 98.4%  | 98.5%    |

**Importance de la feature `conso_m2`** : **45.2%** (dominante)

### 4.5 Synthèse Comparative des Modèles

| Critère                          | Modèle 1 | Modèle 2   | Modèle 3 (Supervisé) | Modèle 3 (Chaîné) |
|----------------------------------|----------|------------|----------------------|-------------------|
| **Accuracy/R²**                  | 79.0%    | 0.872 (R²) | **99.0%**            | 67.0%             |
| **Temps Inférence**              | 45 ms    | 62 ms      | **38 ms**            | 100 ms            |
| **Features Requises**            | 24       | 24         | 24 + conso           | 24                |
| **Cas d'Usage Optimal**          | Estimation préachat | Audit énergétique | Validation DPE | Démo pédagogique |

**Recommandation** : **Modèle 1** pour production (meilleur compromis performance/simplicité)

---

## 5. Validation et Analyse des Performances

### 5.1 Validation Croisée (5-fold Stratifié)

| Modèle                  | Métrique          | Fold 1 | Fold 2 | Fold 3 | Fold 4 | Fold 5 | Moyenne | σ    |
|-------------------------|-------------------|--------|--------|--------|--------|--------|---------|------|
| **Modèle 1**            | F1-Score (macro)  | 76.8%  | 76.2%  | 77.1%  | 75.9%  | 76.4%  | 76.5%   | ±1.8%|
|                         | Accuracy          | 79.3%  | 78.7%  | 79.5%  | 78.4%  | 78.9%  | 78.9%   | ±1.6%|
| **Modèle 2**            | R²                | 0.874  | 0.869  | 0.876  | 0.867  | 0.871  | 0.871   | ±1.2%|
| **Modèle 3 (Supervisé)**| F1-Score (macro)  | 98.8%  | 98.6%  | 98.9%  | 98.5%  | 98.7%  | 98.7%   | ±0.4%|

**Coefficient de Variation** :  
- Modèle 1 : 2.35%     
- Modèle 2 : 1.38%    
- Modèle 3 : 0.41%     

**Stack Technique** :
- Python 3.10+, scikit-learn 1.4+, pandas, numpy
- imbalanced-learn 0.11+ (SMOTE)
- Streamlit, Plotly, FastAPI
- Mistral AI (interprétation LLM)

**Environnement** :
```python
RANDOM_SEED = 42
Train/Test Split : 80% / 20% stratifié
Validation Croisée : 5-fold stratifié
```

---

*Projet Python/MM - M2 SISE - Octobre 2025*
