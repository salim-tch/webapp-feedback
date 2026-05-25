import random
from flask import Flask, render_template_string

app = Flask(__name__)

QUOTES = [
    "« Parfois, le meilleur composant d'un système est l'absence de composant. » — Elon Musk",
    "« Le code, c'est comme l'humour. Quand il faut l'expliquer, c'est qu'il est mauvais. » — Cory House",
    "« Simplicité est la sophistication suprême. » — Léonard de Vinci",
    "« Ne vous inquiétez pas si ça ne marche pas du premier coup. Si tout fonctionnait du premier coup, vous seriez au chômage. » — Loi de Mosher",
    "« L'informatique n'est pas plus une question d'ordinateurs que l'astronomie n'est une question de télescopes. » — Edsger W. Dijkstra"
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Azure Python Test</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #ffffff;
            height: 100vh;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            text-align: center;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            max-width: 500px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        h1 { font-size: 2rem; margin-bottom: 20px; color: #4facfe; }
        p { font-size: 1.2rem; line-height: 1.6; font-style: italic; }
        .btn {
            display: inline-block;
            margin-top: 20px;
            padding: 10px 20px;
            background: #00c6ff;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            transition: 0.3s ease;
        }
        .btn:hover { background: #0072ff; }
        .badge { background: #4caf50; padding: 5px 10px; border-radius: 20px; font-size: 0.8rem; }
    </style>
</head>
<body>
    <div class="container">
        <span class="badge">🚀 Statut : Azure en ligne</span>
        <h1>Test App Service Python</h1>
        <p>{{ quote }}</p>
        <a href="/" class="btn">Inspirer un autre dev</a>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    selected_quote = random.choice(QUOTES)
    return render_template_string(HTML_TEMPLATE, quote=selected_quote)

if __name__ == '__main__':
    # Azure utilise le port 8000 par défaut pour Python, ou la variable d'environnement PORT
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
