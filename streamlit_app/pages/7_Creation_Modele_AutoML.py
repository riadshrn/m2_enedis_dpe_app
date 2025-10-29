import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import joblib
from io import BytesIO
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, f1_score, recall_score, precision_score, confusion_matrix
)
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
import plotly.express as px
import plotly.figure_factory as ff
from pathlib import Path



# === CSS ===
def load_css():
    css_file = Path(__file__).parent.parent / "assets" / "styles.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ---------------------------------------------------------
# ⚙️ Configuration
# ---------------------------------------------------------
st.set_page_config(page_title="AutoML – Création de modèle DPE", page_icon="🤖", layout="wide")
st.title("🤖 AutoML – Création et évaluation automatique de modèles DPE")

# ---------------------------------------------------------
# 🔐 Authentification
# ---------------------------------------------------------
PASSWORD = "enedis2025"
password = st.text_input("🔑 Mot de passe administrateur requis :", type="password")
if password != PASSWORD:
    st.warning("🔒 Accès restreint — entrez le mot de passe pour continuer.")
    st.stop()
st.success("✅ Accès autorisé. Vous pouvez créer et comparer plusieurs modèles.")

# ---------------------------------------------------------
# 🧩 Génération d’un dataset synthétique (10 000 lignes)
# ---------------------------------------------------------
st.markdown("### ⚙️ Génération du dataset synthétique")
if st.button("🧬 Générer un dataset de 10 000 logements aléatoires"):
    with st.spinner("Génération en cours..."):
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
        st.session_state.df_automl = df
        st.success("✅ Dataset synthétique de 10 000 lignes généré avec succès !")

if "df_automl" not in st.session_state:
    st.stop()

df = st.session_state.df_automl
st.dataframe(df.head(), use_container_width=True)
st.info("💡 Le modèle tentera de prédire la colonne **etiquette_dpe**.")

# ---------------------------------------------------------
# 🧠 AutoML
# ---------------------------------------------------------
if st.button("🚀 Lancer la création et l’évaluation des modèles"):
    with st.spinner("Entraînement et évaluation en cours..."):
        start_time = time.time()

        X = df.drop(columns=["etiquette_dpe"])
        y = df["etiquette_dpe"]
        X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)
        st.session_state.X_test = X_test
        st.session_state.y_test = y_test

        numeric_features = ["volume_logement", "hauteur_sous_plafond", "nombre_niveau_logement",
                            "anciennete", "score_isolation_moyen", "conso_m2"]
        categorical_features = ["isolation_toiture", "qualite_isolation_murs", "qualite_isolation_menuiseries",
                                "type_energie_principale_chauffage", "energie_regroupee",
                                "type_logement_source", "classe_annee_construction"]

        preprocessor = ColumnTransformer([
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
        ])

        models = {
            "RandomForestClassifier": RandomForestClassifier(n_estimators=300, max_depth=25, random_state=42, n_jobs=-1),
            "DecisionTreeClassifier": DecisionTreeClassifier(max_depth=20, random_state=42),
            "GradientBoostingClassifier": GradientBoostingClassifier(random_state=42),
            "AdaBoostClassifier": AdaBoostClassifier(random_state=42),
            "LogisticRegression": LogisticRegression(max_iter=500, random_state=42),
            "KNeighborsClassifier": KNeighborsClassifier(n_neighbors=7),
            "SVC (RBF kernel)": SVC(kernel="rbf", gamma="scale", random_state=42)
        }

        results = []
        models_trained = {}

        for name, clf in models.items():
            start = time.time()
            pipe = Pipeline([("preprocessor", preprocessor), ("classifier", clf)])
            pipe.fit(X_train, y_train)
            y_pred = pipe.predict(X_test)
            elapsed = time.time() - start

            results.append({
                "Modèle": name,
                "Accuracy": round(accuracy_score(y_test, y_pred), 3),
                "F1-macro": round(f1_score(y_test, y_pred, average="macro"), 3),
                "Recall": round(recall_score(y_test, y_pred, average="macro"), 3),
                "Précision": round(precision_score(y_test, y_pred, average="macro"), 3),
                "Temps (s)": round(elapsed, 2)
            })
            models_trained[name] = (pipe, y_pred)

        df_results = pd.DataFrame(results).sort_values(by="F1-macro", ascending=False)
        st.session_state.df_results = df_results
        st.session_state.models_trained = models_trained
        st.success(f"✅ Évaluation terminée en {time.time() - start_time:.1f} secondes.")

# ---------------------------------------------------------
# 📊 Résultats comparatifs + sélection d’un modèle
# ---------------------------------------------------------
if "df_results" in st.session_state:
    df_results = st.session_state.df_results
    models_trained = st.session_state.models_trained

    st.markdown("### 📊 Tableau comparatif des performances")
    st.dataframe(df_results, use_container_width=True)

    fig = px.bar(
        df_results,
        x="Modèle",
        y="F1-macro",
        color="F1-macro",
        color_continuous_scale="YlOrRd",
        title="F1-macro par modèle",
        text="F1-macro"
    )
    fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
    fig.update_layout(xaxis_title="", yaxis_title="F1-macro", height=500)
    st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------------------------------
    # 🔍 Inspection d’un modèle spécifique
    # ---------------------------------------------------------
    selected_model = st.selectbox("🔎 Sélectionnez un modèle à inspecter :", df_results["Modèle"])

    if selected_model:
        model, y_pred = models_trained[selected_model]
        X = st.session_state.df_automl.drop(columns=["etiquette_dpe"])
        y = st.session_state.df_automl["etiquette_dpe"]

        st.markdown(f"### 📄 Fiche du modèle : **{selected_model}**")
        row = df_results[df_results["Modèle"] == selected_model].iloc[0]
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Accuracy", row["Accuracy"])
        c2.metric("F1-macro", row["F1-macro"])
        c3.metric("Recall", row["Recall"])
        c4.metric("Précision", row["Précision"])
        c5.metric("Temps (s)", row["Temps (s)"])

        # Matrice de confusion
        st.markdown("#### 🔢 Matrice de confusion")

        y_test = st.session_state.y_test
        cm = confusion_matrix(y_test, y_pred, labels=["A", "B", "C", "D", "E", "F", "G"])

        fig_cm = ff.create_annotated_heatmap(
            z=cm.astype(int),
            x=["A", "B", "C", "D", "E", "F", "G"],
            y=["A", "B", "C", "D", "E", "F", "G"],
            colorscale="Blues",
            showscale=True
        )
        fig_cm.update_layout(
            title=f"Matrice de confusion – {selected_model}",
            xaxis_title="Prédit",
            yaxis_title="Réel",
            height=500
        )
        st.plotly_chart(fig_cm, use_container_width=True)

        # Téléchargement du modèle
        st.markdown("#### 💾 Télécharger ce modèle")
        buf = BytesIO()
        joblib.dump(model, buf, compress=("xz", 6))
        buf.seek(0)
        st.download_button(
            "📥 Télécharger le modèle sélectionné (.joblib)",
            data=buf,
            file_name=f"{selected_model}_trained.joblib",
            mime="application/octet-stream",
            use_container_width=True
        )
