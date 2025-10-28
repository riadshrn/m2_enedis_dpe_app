import joblib
import requests
from pathlib import Path
from tqdm import tqdm 

MODELS_PATH = Path(__file__).resolve().parent.parent / "app" / "models" / "Compressed"
MODELS_PATH.mkdir(parents=True, exist_ok=True)

# === URLs Hugging Face ===
urls = {
    "rf_dpe_sans_conso": "https://huggingface.co/spaces/riadshrn/dpe_model-v2/resolve/main/rf_dpe_sans_conso_compressed.joblib",
    "rf_dpe_avec_conso": "https://huggingface.co/spaces/riadshrn/dpe_model-v2/resolve/main/rf_dpe_avec_conso_compressed.joblib",
    "rf_conso_final": "https://huggingface.co/spaces/riadshrn/models-dpe/resolve/main/rf_conso_final_compressed.joblib"
}

models = {}

for name, url in urls.items():
    fpath = MODELS_PATH / f"{name}_compressed.joblib"

    try:
        # === Téléchargement avec barre de progression ===
        if not fpath.exists():
            print(f"📦 Téléchargement de {name} depuis Hugging Face...")
            response = requests.get(url, stream=True, timeout=(10, 180))
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            block_size = 1024  
            progress_bar = tqdm(
                total=total_size,
                unit="iB",
                unit_scale=True,
                desc=f"{name}",
                ncols=80,
                colour="green"
            )

            with open(fpath, "wb") as f:
                for chunk in response.iter_content(block_size):
                    progress_bar.update(len(chunk))
                    f.write(chunk)
            progress_bar.close()

            if total_size != 0 and progress_bar.n != total_size:
                print(f"⚠️ Téléchargement incomplet pour {name}.")
            else:
                print(f"✅ {name} téléchargé avec succès.")

        # === Chargement du modèle ===
        print(f"🧠 Chargement du modèle {name}...")
        models[name] = joblib.load(fpath)
        print(f"✅ {name} chargé ({fpath.name})")

    except requests.exceptions.Timeout:
        print(f"⏱️ Timeout : téléchargement trop long pour {name}.")
    except Exception as e:
        print(f"❌ Erreur lors du chargement de {name}: {e}")

print("\n🚀 Tous les modèles sont prêts !")