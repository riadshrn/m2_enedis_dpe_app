FROM python:3.11-slim

# ========= Dépendances système =========
RUN apt-get update && apt-get install -y \
    build-essential \
    libopenblas-dev \
    liblapack-dev \
    gfortran \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# ========= Répertoire de travail =========
WORKDIR /app

# ========= Copier et installer les dépendances Python =========
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# ========= Copier le reste du code =========
COPY . .

# ========= Correction Streamlit Permissions =========
# Créer le dossier accessible /tmp/.streamlit pour éviter PermissionError
RUN mkdir -p /tmp/.streamlit && \
    echo "[browser]\ngatherUsageStats = false" > /tmp/.streamlit/config.toml

# ========= Variables d’environnement =========
# Définir le dossier HOME et Chrome pour Kaleido
ENV HOME=/tmp
ENV CHROME_PATH=/usr/bin/chromium

# ========= Exposition du port Streamlit =========
EXPOSE 8501

# ========= Commande de démarrage =========
CMD ["streamlit", "run", "Accueil.py", "--server.port=8501", "--server.address=0.0.0.0"]
