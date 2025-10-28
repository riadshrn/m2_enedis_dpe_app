# ⚡ Streamlit - Démarrage Rapide (2 minutes)

## 🎯 En 3 commandes

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Lancer l'application
streamlit run app_streamlit.py

# 3. Ouvrir dans le navigateur
# → http://localhost:8501 (s'ouvre automatiquement)
```

**C'est tout ! 🎉**

---

## 📊 Premier graphique en 1 minute

### Option CSV (plus simple)

1. **Cliquez** sur "Browse files" dans la barre latérale
2. **Uploadez** votre CSV
3. **Sélectionnez** :
   - Type : `scatter`
   - X : (une colonne numérique)
   - Y : (une autre colonne numérique)
4. **Cliquez** sur "🚀 Générer le graphique"

### Option API (pour tester)

1. **Sélectionnez** "🌐 API REST" dans la barre latérale
2. **Copiez-collez** cette URL :
   ```
   https://jsonplaceholder.typicode.com/users
   ```
3. **Cliquez** sur "🔄 Charger les données"
4. **Sélectionnez** :
   - Type : `scatter`
   - X : `id`
   - Y : (choisissez une colonne)
5. **Cliquez** sur "🚀 Générer le graphique"

---

## 🔗 APIs de test

Copiez-collez ces URLs pour tester immédiatement :

### 1. Utilisateurs
```
https://jsonplaceholder.typicode.com/users
```

### 2. Cryptomonnaies
```
https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&per_page=50
```

### 3. COVID-19
```
https://disease.sh/v3/covid-19/countries
```

---

## 💡 Astuces rapides

### Graphiques recommandés par type de données

**Relation entre 2 variables** → `scatter`
**Évolution temporelle** → `line`
**Comparaison catégories** → `bar`
**Distribution** → `histogram` ou `box`
**Proportions** → `pie`

### Options de personnalisation

- **Couleur** : Sélectionnez une colonne catégorielle
- **Taille** : Sélectionnez une colonne numérique
- **Hover** : Ajoutez des infos au survol

---

## 🎨 Exemple complet

Pour visualiser la relation entre deux variables avec segmentation :

1. **Type** : `scatter`
2. **X** : Variable numérique 1
3. **Y** : Variable numérique 2
4. **Z** : Variable catégorielle (crée des sous-graphiques)
5. **Couleur** : Même variable que Z ou différente
6. **Générer** !

---

## ❓ Problèmes ?

### Application ne démarre pas
```bash
# Vérifier l'installation
pip install streamlit plotly pandas

# Relancer
streamlit run app_streamlit.py
```

### Port déjà utilisé
```bash
# Utiliser un autre port
streamlit run app_streamlit.py --server.port 8502
```

### Module non trouvé
```bash
# Installer toutes les dépendances
pip install -r requirements.txt
```

---

## 📚 Aller plus loin

- **Documentation complète** : `README_STREAMLIT.md`
- **Configuration graphiques** : `README.md`
- **Support PNG** : `GUIDE_PNG.md`

---

**Prêt à visualiser vos données ? Lancez l'application ! 🚀**

```bash
streamlit run app_streamlit.py
```
