import os
import uuid
import json  # 👈 Ajouté pour structurer les données envoyées à la fonction
import urllib.request  # 👈 Ajouté pour appeler l'URL de l'Azure Function sans dépendance externe
from flask import Flask, render_template_string, request, redirect
from azure.cosmos import CosmosClient, exceptions, PartitionKey

app = Flask(__name__)

# --- CONFIGURATION COSMOS DB ---
CONNECTION_STRING = os.environ.get("COSMOS_CONNECTION_STRING")
cosmos_status = "❌ Non configuré"
container = None

if CONNECTION_STRING:
    try:
        # Initialisation du client Cosmos
        client = CosmosClient.from_connection_string(CONNECTION_STRING)
        # Création ou récupération de la base de données
        db = client.create_database_if_not_exists(id="FeedbackDB")
        
        # Utilisation de l'objet PartitionKey officiel
        container = db.create_container_if_not_exists(
            id="Feedbacks", 
            partition_key=PartitionKey(path="/id")
        )
        cosmos_status = "✅ Connecté à Cosmos DB"
    except Exception as e:
        cosmos_status = f"⚠️ Erreur de connexion : {str(e)}"

# --- INTERFACE HTML ATTRACTIVE ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Application Feedback - Python</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #1f4037 0%, #99f2c8 100%);
            color: #333;
            min-height: 100vh;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
            width: 100%;
            max-width: 500px;
        }
        h1 { color: #1f4037; margin-top: 0; text-align: center; }
        .badge {
            display: block;
            text-align: center;
            padding: 8px;
            background: #eee;
            border-radius: 6px;
            font-size: 0.9rem;
            margin-bottom: 20px;
            font-weight: bold;
        }
        .status-success { background: #d4edda; color: #155724; }
        .status-error { background: #f8d7da; color: #721c24; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: #555; }
        input[type="text"], textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 6px;
            box-sizing: border-box;
        }
        textarea { height: 100px; resize: none; }
        .btn {
            width: 100%;
            padding: 12px;
            background: #1f4037;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 1rem;
            cursor: pointer;
            font-weight: bold;
            transition: background 0.2s;
        }
        .btn:hover { background: #142a24; }
        .message-box {
            padding: 10px;
            margin-bottom: 15px;
            border-radius: 6px;
            text-align: center;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Formulaire de Feedback</h1>
        
        <div class="badge {% if '✅' in status %}status-success{% else %}status-error{% endif %}">
            Statut Base : {{ status }}
        </div>

        {% if msg %}
            <div class="message-box status-success">{{ msg }}</div>
        {% endif %}

        <form method="POST" action="/submit">
            <div class="form-group">
                <label for="nom">Votre Nom :</label>
                <input type="text" id="nom" name="nom" required placeholder="Ex: Salim">
            </div>
            <div class="form-group">
                <label for="commentaire">Votre Commentaire :</label>
                <textarea id="commentaire" name="commentaire" required placeholder="Laissez votre message ici..."></textarea>
            </div>
            <button type="submit" class="btn" {% if not connected %}disabled style="background:#ccc;"{% endif %}>
                {% if connected %}Envoyer le Feedback{% else %}Base déconnectée{% endif %}
            </button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    msg = request.args.get('msg', '')
    is_connected = container is not None
    return render_template_string(HTML_TEMPLATE, status=cosmos_status, connected=is_connected, msg=msg)

@app.route('/submit', methods=['POST'])
def submit():
    if container:
        nom = request.form.get('nom')
        commentaire = request.form.get('commentaire')
        
        feedback_item = {
            "id": str(uuid.uuid4()),
            "nom": nom,
            "commentaire": commentaire
        }
        
        try:
            # 1. Enregistrement initial dans Cosmos DB
            container.create_item(body=feedback_item)
            
            # 2. 🚀 APPEL DE VOTRE AZURE FUNCTION HTTP
            url_function = "https://feedback-function-cdp-cyf6ehgwc9adgybu.westus3-01.azurewebsites.net/api/SendThankYouEmail"
            
            # Structuration de la charge utile JSON attendue par la fonction Node.js (req.body.email)
            payload = json.dumps({"email": nom}).encode('utf-8')
            
            # Envoi de la requête POST
            req_azure = urllib.request.Request(
                url_function, 
                data=payload, 
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            # On exécute l'appel en fermant directement la connexion
            with urllib.request.urlopen(req_azure, timeout=5) as response:
                pass
                
            return redirect("/?msg=Feedback enregistré et e-mail simulé avec succès !")
        except Exception as e:
            return f"Erreur lors de l'exécution : {str(e)}"
            
    return redirect("/")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
