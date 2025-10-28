# app/schemas.py
from pydantic import BaseModel
from typing import Optional

# ⚙️ Features communes
class BaseFeatures(BaseModel):
    volume_logement: float
    hauteur_sous_plafond: float
    nombre_niveau_logement: int
    anciennete: float
    isolation_toiture: str
    score_isolation_moyen: float
    qualite_isolation_murs: str
    qualite_isolation_menuiseries: str
    type_energie_principale_chauffage: str
    energie_regroupee: str
    type_logement_source: str
    classe_annee_construction: str
    surface_habitable_logement: float

# Modèle pour prédiction DPE sans conso
class DpeSansConsoFeatures(BaseFeatures):
    # On enlève conso_m2 et etiquette_dpe_regroupee
    volume_logement: float
    hauteur_sous_plafond: float
    nombre_niveau_logement: int
    anciennete: float
    isolation_toiture: str
    score_isolation_moyen: float
    qualite_isolation_murs: str
    qualite_isolation_menuiseries: str
    type_energie_principale_chauffage: str
    energie_regroupee: str
    type_logement_source: str
    classe_annee_construction: str
    pass

# Modèle pour prédiction DPE avec conso renseignée
class DpeAvecConsoFeatures(BaseFeatures):
    volume_logement: float
    hauteur_sous_plafond: float
    nombre_niveau_logement: int
    anciennete: float
    isolation_toiture: str
    score_isolation_moyen: float
    qualite_isolation_murs: str
    qualite_isolation_menuiseries: str
    type_energie_principale_chauffage: str
    energie_regroupee: str
    type_logement_source: str
    classe_annee_construction: str
    conso_m2: float  

# Modèle pour prédiction de la conso (on ne connaît pas conso_m2 ni étiquette)
class ConsoFeatures(BaseFeatures):
    volume_logement: float
    hauteur_sous_plafond: float
    nombre_niveau_logement: int
    anciennete: float
    isolation_toiture: str
    score_isolation_moyen: float
    qualite_isolation_murs: str
    qualite_isolation_menuiseries: str
    type_energie_principale_chauffage: str
    energie_regroupee: str
    type_logement_source: str
    classe_annee_construction: str
    surface_habitable_logement: float
    pass

# Pour l’interprétation (appel Mistral)
class InterpretationRequest(BaseModel):
    volume_logement: float
    hauteur_sous_plafond: float
    nombre_niveau_logement: int
    anciennete: float
    isolation_toiture: str
    score_isolation_moyen: float
    qualite_isolation_murs: str
    qualite_isolation_menuiseries: str
    type_energie_principale_chauffage: str
    energie_regroupee: str
    type_logement_source: str
    classe_annee_construction: str
    surface_habitable_logement: float  
    conso_m2: float                    
    etiquette_dpe_regroupee: Optional[str] = None
    nom_commune: Optional[str] = None   
