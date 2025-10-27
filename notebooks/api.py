from flask import Flask, jsonify, request
import joblib
import pandas as pd

# ======================================================
# ⚙️ 1. Initialiser l'application Flask
# ======================================================
app = Flask(__name__)

# ======================================================
# ⚙️ 2. Charger le modèle de classification
# ======================================================
# Remplace par ton fichier modèle (ex : "classification_model.joblib")
MODEL_PATH = "classification_model.joblib"

try:
    model = joblib.load(MODEL_PATH)
    print(f"✅ Modèle chargé : {MODEL_PATH}")
except Exception as e:
    model = None
    print(f"⚠️ Impossible de charger le modèle : {e}")

# ======================================================
# ⚙️ 3. Route de bienvenue (GET)
# ======================================================
@app.route('/api/welcome', methods=['GET'])
def welcome():
    return jsonify({"message": "Bienvenue sur l'API de classification!"})

# ======================================================
# ⚙️ 4. Route de prédiction (POST)
# ======================================================
@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Exemple de requête POST (JSON attendu) :
    {
        "features": {
            "col1": valeur,
            "col2": valeur,
            ...
        }
    }
    """
    if model is None:
        return jsonify({"error": "Le modèle n'est pas chargé"}), 500

    try:
        data = request.get_json()
        features = data.get("features")

        if not features:
            return jsonify({"error": "Aucune donnée fournie"}), 400

        # Conversion en DataFrame (1 ligne)
        df = pd.DataFrame([features])

        # Prédiction
        prediction = model.predict(df)[0]

        # Probabilités (si disponible)
        try:
            proba = model.predict_proba(df).tolist()[0]
            return jsonify({
                "prediction": str(prediction),
                "probabilities": proba
            })
        except:
            return jsonify({"prediction": str(prediction)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ======================================================
# ⚙️ 5. Lancer le serveur local
# ======================================================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
