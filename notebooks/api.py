from flask import Flask, jsonify, request

# Initialiser l'application Flask
app = Flask(__name__)

# Route 1 : Récupérer un message de bienvenue
@app.route('/api/welcome', methods=['GET'])
def welcome():
    return jsonify({"message": "Bienvenue sur l'API!"})   

# Lancer l'API en local
if __name__ == '__main__':
    app.run(debug=True, port=5000)