import requests
import streamlit as st

# URL de votre API FastAPI
API_BASE_URL = "https://riadshrn-api-dpe-conso.hf.space"  
#API_BASE_URL = "http://localhost:8000"

def call_api(endpoint: str, data: dict):
    """
    Appelle l'API FastAPI
    
    Args:
        endpoint (str): Route de l'API (ex: "/predict/dpe_sans_conso")
        data (dict): Données à envoyer
    
    Returns:
        dict: Résultat de l'API ou None en cas d'erreur
    """
    try:
        response = requests.post(f"{API_BASE_URL}{endpoint}", json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error("⏱️ Timeout: L'API met trop de temps à répondre")
        return None
    except requests.exceptions.ConnectionError:
        st.error("🔌 Erreur de connexion: Vérifiez que l'API est démarrée")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ Erreur HTTP {e.response.status_code}: {e.response.text}")
        return None
    except Exception as e:
        st.error(f"❌ Erreur inattendue: {str(e)}")
        return None

def set_api_url(url: str):
    """
    Modifie l'URL de base de l'API
    """
    global API_BASE_URL
    API_BASE_URL = url

