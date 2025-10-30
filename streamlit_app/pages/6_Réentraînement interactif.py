# pages/8_Réentraînement_interactif.py
import streamlit as st
import pandas as pd
import joblib
import numpy as np
import random
from io import BytesIO
import plotly.express as px
import plotly.figure_factory as ff
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from pathlib import Path
from sklearn.model_selection import train_test_split
from utils.layout import render_sidebar, load_css

# Charger les styles et la sidebar commune
load_css()
render_sidebar()


# === CONFIG GÉNÉRALE ===
logo_path = Path(__file__).parent.parent / "assets" / "logo-removebg.png"
# ========= CONFIG & STYLES =========
st.set_page_config(
    page_title="Réentraînement modèle DPE",
    page_icon=logo_path,
    layout="wide"
)
st.title("Réentraînement interactif du modèle DPE")

# ------------------------------------------------------------
# Authentification
# ------------------------------------------------------------
PASSWORD = "enedis2025"
password = st.text_input(" Mot de passe administrateur requis :", type="password")
if password != PASSWORD:
    st.warning("Accès restreint — entrez le mot de passe pour continuer.")
    st.stop()
st.success("Accès autorisé. Vous pouvez réentraîner le modèle.")

# ------------------------------------------------------------
# Import ou génération des données
# ------------------------------------------------------------
st.markdown("### Importer ou générer un jeu de données")

uploaded_file = st.file_uploader("Importer un fichier CSV d'entraînement", type=["csv"])

# Utiliser st.session_state pour retenir le dataset généré
if "df_data" not in st.session_state:
    st.session_state.df_data = None

# Si un fichier est uploadé
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.session_state.df_data = df
    st.success("Fichier chargé avec succès depuis votre ordinateur.")

# Sinon, bouton pour générer un dataset
elif st.button("Générer un dataset synthétique (10000 lignes)"):
    with st.spinner("Génération du dataset synthétique en cours..."):
        np.random.seed(42)
        rows = []
        classes = ["A", "B", "C", "D", "E", "F", "G"]
        years = ["avant_1948", "1949_1974", "1975_1989", "1990_1999", "2000_2011", "apres_2012"]
        energies = ["GAZ NATUREL", "ÉLECTRICITÉ",
                    "ÉLECTRICITÉ D'ORIGINE RENOUVELABLE UTILISÉE DANS LE BÂTIMENT",
                    "BOIS – BÛCHES", "FIOUL DOMESTIQUE", "RÉSEAU DE CHAUFFAGE URBAIN"]
        isolations = ["INSUFFISANTE", "MOYENNE", "BONNE", "TRÈS BONNE"]

        for _ in range(10000):
            etiquette = random.choices(classes, weights=[8, 12, 20, 25, 15, 12, 8])[0]
            anciennete = np.random.randint(5, 80)
            hauteur = round(np.random.uniform(2.3, 2.9), 1)
            surface = np.random.randint(50, 200)
            niveau = np.random.choice([1, 2])
            volume = surface * hauteur * 0.5
            conso = np.random.normal(
                {"A": 100, "B": 130, "C": 170, "D": 190, "E": 220, "F": 250, "G": 280}[etiquette], 10)
            score_iso = np.clip(1 - (conso / 300), 0.4, 0.95)

            rows.append([
                volume, hauteur, niveau, anciennete, np.random.choice([0, 1]),
                round(score_iso, 2),
                np.random.choice(isolations), np.random.choice(isolations),
                np.random.choice(energies),
                random.choice(["gaz", "fioul", "bois", "electrique", "autre"]),
                np.random.choice(["EXISTANT", "NEUF"]),
                np.random.choice(years),
                surface,
                round(conso, 1),
                etiquette
            ])

        cols = ["volume_logement", "hauteur_sous_plafond", "nombre_niveau_logement", "anciennete",
                "isolation_toiture", "score_isolation_moyen", "qualite_isolation_murs",
                "qualite_isolation_menuiseries", "type_energie_principale_chauffage",
                "energie_regroupee", "type_logement_source", "classe_annee_construction",
                "surface_habitable_logement", "conso_m2", "etiquette_dpe"]

        df = pd.DataFrame(rows, columns=cols)
        st.session_state.df_data = df
        st.success("Dataset synthétique généré avec succès !")

# Récupérer le dataset persistant (uploadé ou généré)
df = st.session_state.df_data

# ------------------------------------------------------------
# Visualisation du dataset
# ------------------------------------------------------------
if df is not None:
    st.markdown("### Aperçu des données disponibles")
    st.dataframe(df, width="stretch", height=300)
    st.info("La variable cible utilisée pour l'entraînement est **`etiquette_dpe`**.")

    # --------------------------------------------------------
    # Réentraînement du modèle
    # --------------------------------------------------------
    X = df.drop(columns=["etiquette_dpe"])
    y = df["etiquette_dpe"]

    if st.button("Lancer le réentraînement sur ces données"):
        with st.spinner("Préparation et initialisation du modèle..."):
            import time
            progress = st.progress(0)
            for i in range(0, 30):
                time.sleep(0.05)  # simulate un petit délai (réalisme)
                progress.progress(i + 1)
            progress.empty()

        with st.spinner("Entraînement du modèle en cours..."):
            import time
            progress = st.progress(0)

            # === Split des données ===
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, stratify=y, random_state=42
            )

            # === Préprocesseur ===
            numeric_features = ["volume_logement", "hauteur_sous_plafond", "nombre_niveau_logement",
                                "anciennete", "score_isolation_moyen", "conso_m2"]
            numeric_transformer = StandardScaler()

            categorical_features = ["isolation_toiture", "qualite_isolation_murs", "qualite_isolation_menuiseries",
                                    "type_energie_principale_chauffage", "energie_regroupee",
                                    "type_logement_source", "classe_annee_construction"]
            categorical_transformer = OneHotEncoder(handle_unknown="ignore")

            preprocessor = ColumnTransformer(
                transformers=[
                    ("num", numeric_transformer, numeric_features),
                    ("cat", categorical_transformer, categorical_features)
                ]
            )

            # === Modèle ===
            rf_dpe_conso = Pipeline([
                ("preprocessor", preprocessor),
                ("classifier", RandomForestClassifier(
                    n_estimators=300,
                    max_depth=25,
                    min_samples_split=5,
                    random_state=42,
                    n_jobs=-1
                ))
            ])

            # Simulation de progression visuelle de l'entraînement
            for i in range(0, 100):
                time.sleep(0.03)  # ralentir un peu pour donner l’impression de calcul
                progress.progress(i + 1 if i < 99 else 100)

            # === Entraînement réel ===
            rf_dpe_conso.fit(X_train, y_train)

            progress.empty()

        st.success("Réentraînement terminé avec succès !")


        # --------------------------------------------------------
        # Évaluation sur le jeu de test
        # --------------------------------------------------------
        y_pred = rf_dpe_conso.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        f1_macro = f1_score(y_test, y_pred, average="macro")
        f1_weighted = f1_score(y_test, y_pred, average="weighted")

        # --------------------------------------------------------
        # Dimensions des jeux de données
        # --------------------------------------------------------
        train_size = len(X_train)
        test_size = len(X_test)
        total_size = len(X)
        train_pct = train_size / total_size * 100
        test_pct = test_size / total_size * 100

        c1, c2, c3, c4, c5 = st.columns(5)

        # Métriques principales
        c1.metric("Accuracy (test)", f"{acc:.3f}")
        c2.metric("F1 Macro", f"{f1_macro:.3f}")
        c3.metric("F1 Pondéré", f"{f1_weighted:.3f}")

        # Informations sur les splits
        c4.markdown(f"**Jeu d'entraînement :** {train_size:,} lignes  \n({train_pct:.1f}%)")
        c5.markdown(f"**Jeu de test :** {test_size:,} lignes  \n({test_pct:.1f}%)")

        # Rapport détaillé
        report = classification_report(y_test, y_pred, output_dict=True)
        report_df = pd.DataFrame(report).transpose()
        st.markdown("### Rapport de classification (jeu de test)")

        markdown_report = "#### Résumé des performances par classe\n\n"
        markdown_report += "| Classe | Précision | Rappel | F1-score | Support |\n"
        markdown_report += "|:------:|:----------:|:-------:|:---------:|:--------:|\n"

        for label in ["A","B","C","D","E","F","G"]:
            if label in report:
                p = report[label]["precision"]
                r = report[label]["recall"]
                f = report[label]["f1-score"]
                s = report[label]["support"]
                markdown_report += f"| **{label}** | **{p:.2f}** | **{r:.2f}** | **{f:.2f}** | {int(s)} |\n"


        st.markdown(markdown_report)

        # Définition du mapping des couleurs DPE (si pas déjà défini plus haut)
        dpe_color_map = {
            "A": "#00FF00",   # Vert
            "B": "#7FFF00",   # Vert clair
            "C": "#FFFF00",   # Jaune
            "D": "#FFD700",   # Or
            "E": "#FFA500",   # Orange
            "F": "#FF4500",   # Rouge orangé
            "G": "#FF0000"    # Rouge vif
        }

        # Graphique F1-score par classe avec couleurs DPE
        f1_per_class = report_df.loc[["A", "B", "C", "D", "E", "F", "G"], "f1-score"].dropna()

        fig_f1 = px.bar(
            f1_per_class,
            x=f1_per_class.index,
            y=f1_per_class.values,
            title="F1-score par étiquette DPE (jeu de test)",
            color=f1_per_class.index,
            color_discrete_map=dpe_color_map,
            labels={"x": "Étiquette DPE", "y": "F1-score"}
        )

        fig_f1.update_traces(text=f1_per_class.round(2), textposition="outside")
        fig_f1.update_layout(
            xaxis_title="Étiquette DPE",
            yaxis_title="F1-score",
            margin=dict(l=0, r=0, t=60, b=0),
            showlegend=False
        )

        st.plotly_chart(fig_f1, use_container_width=True)

        # Matrice de confusion
        cm = confusion_matrix(y_test, y_pred, labels=["A", "B", "C", "D", "E", "F", "G"])
        fig_cm = ff.create_annotated_heatmap(
            z=cm.astype(int),
            x=["A", "B", "C", "D", "E", "F", "G"],
            y=["A", "B", "C", "D", "E", "F", "G"],
            colorscale="YlGnBu",
            showscale=True
        )
        fig_cm.update_layout(title="Matrice de confusion (jeu de test)",
                            xaxis_title="Prédit", yaxis_title="Réel")
        st.plotly_chart(fig_cm, use_container_width=True)

        # --------------------------------------------------------
        # Téléchargement du modèle réentraîné
        # --------------------------------------------------------
        with st.spinner("Compression du modèle en cours..."):
            buf = BytesIO()

            # Barre de progression visuelle
            progress_text = "Préparation du modèle téléchargeable..."
            my_bar = st.progress(0, text=progress_text)

            # Compression + simulation d’un léger délai pour l’effet visuel
            for percent_complete in range(0, 101, 10):
                time.sleep(0.1) 
                my_bar.progress(percent_complete, text=progress_text)

            joblib.dump(rf_dpe_conso, buf)
            buf.seek(0)
            my_bar.empty()  # Supprime la barre une fois terminé

        st.success("Modèle prêt au téléchargement !")

        st.download_button(
            "Télécharger le modèle réentraîné (.joblib)",
            data=buf,
            file_name="rf_dpe_avec_conso_retrained.joblib",
            mime="application/octet-stream",
            use_container_width=True
        )

else:
    st.info("Importez un fichier ou cliquez sur « Générer un dataset synthétique » pour continuer.")
