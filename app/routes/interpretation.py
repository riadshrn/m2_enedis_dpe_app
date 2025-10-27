from fastapi import APIRouter
from app.mistral_client import get_interpretation
from app.schemas import InterpretationRequest
from app.data_loader import df_communes

router = APIRouter(prefix="/interpretation", tags=["LLM Interprétation"])

@router.post("/")
def interpret_result(data: InterpretationRequest):
    commune_info = ""

    # Calcul de la conso totale à partir de la surface
    conso_totale_mwh = (data.conso_m2 * data.surface_habitable_logement) / 1000

    # --- Recherche des données de la commune ---
    if data.nom_commune:
        commune_name = data.nom_commune.strip().upper()
        if not df_communes.empty and commune_name in df_communes["nom_commune"].unique():
            df_c = df_communes[df_communes["nom_commune"] == commune_name]
            moyenne = df_c["conso_moy_commune_mwh"].mean()
            classe = df_c["classe_conso"].iloc[0] if "classe_conso" in df_c.columns else "inconnue"

            commune_info = (
                f"Dans la commune de {commune_name}, la consommation énergétique moyenne "
                f"est de {moyenne:.2f} MWh/an. Cette commune est classée '{classe}'.\n"
                f"Votre logement consomme environ {conso_totale_mwh:.2f} MWh/an "
                f"({data.conso_m2} kWh/m² pour {data.surface_habitable_logement} m²), "
                f"soit {'en dessous' if conso_totale_mwh < moyenne else 'au-dessus'} de la moyenne communale.\n\n"
            )
        else:
            commune_info = f"Aucune donnée énergétique trouvée pour la commune '{commune_name}'.\n\n"

    # --- Construction du prompt enrichi ---
    prompt = (
        f"{commune_info}"
        f"Voici les caractéristiques du logement :\n"
        f"- Surface habitable : {data.surface_habitable_logement} m²\n"
        f"- Volume du logement : {data.volume_logement} m³\n"
        f"- Hauteur sous plafond : {data.hauteur_sous_plafond} m\n"
        f"- Nombre de niveaux : {data.nombre_niveau_logement}\n"
        f"- Ancienneté du bâtiment : {data.anciennete} ans\n"
        f"- Isolation toiture : {data.isolation_toiture}\n"
        f"- Score d’isolation moyen : {data.score_isolation_moyen}\n"
        f"- Qualité d’isolation des murs : {data.qualite_isolation_murs}\n"
        f"- Qualité d’isolation des menuiseries : {data.qualite_isolation_menuiseries}\n"
        f"- Type d’énergie principale de chauffage : {data.type_energie_principale_chauffage}\n"
        f"- Énergie regroupée : {data.energie_regroupee}\n"
        f"- Type de logement : {data.type_logement_source}\n"
        f"- Classe d’année de construction : {data.classe_annee_construction}\n"
        f"- Consommation énergétique au m² : {data.conso_m2} kWh/m²\n"
        f"- Étiquette DPE prédite : {data.etiquette_dpe_regroupee}\n\n"
        f"Explique de manière claire, synthétique et pédagogique ce que signifient ces résultats "
        f"en tenant compte du contexte énergétique local de la commune du Rhône. "
        f"Détaille uniquement :\n"
        f"01. L’analyse du logement et de sa performance énergétique.\n"
        f"02. Les points forts et faibles du logement.\n"
        f"03. Les pistes d’amélioration possibles (isolation, chauffage, énergies renouvelables).\n"
        f"04. Une conclusion claire.\n\n"
        f"!!!!!! Ne propose pas d’audit énergétique, de diagnostic ou de contact professionnel. "
        f"Ne mentionne pas de services externes ou d’aides financières. "
        f"Ne conclus pas par une phrase publicitaire, seulement par une synthèse finale du résultat."
    )

    interpretation = get_interpretation(prompt)

    return {
        "commune": data.nom_commune,
        "conso_totale_mwh": round(conso_totale_mwh, 2),
        "prompt_envoye": prompt,
        "interpretation": interpretation
    }