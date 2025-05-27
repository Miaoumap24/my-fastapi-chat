from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import asyncio

app = FastAPI()

# Pour servir le fichier HTML, nous allons le mettre dans un dossier 'static'
# Crée un dossier 'static' au même niveau que main.py
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Liste pour stocker toutes les connexions WebSocket actives
active_connections: list[WebSocket] = []

# Liste pour stocker l'historique des messages
message_history: list[str] = []

@app.get("/")
async def get_chat_page():
    """Charge la page HTML du chat."""
    with open(BASE_DIR / "static" / "index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Gère la connexion WebSocket."""
    await websocket.accept()
    active_connections.append(websocket)
    print(f"Nouvelle connexion WebSocket: {websocket.client}")

    # Envoyer l'historique des messages au nouveau client
    for message in message_history:
        await websocket.send_text(message)

    try:
        while True:
            data = await websocket.receive_text()
            print(f"Message reçu de {websocket.client}: {data}")

            # Ajouter le message à l'historique
            message_history.append(data)
            # Limiter l'historique pour ne pas surcharger (ex: 50 derniers messages)
            if len(message_history) > 50:
                message_history.pop(0) # Supprimer le plus ancien

            # Diffuser le message à tous les clients connectés
            for connection in active_connections:
                if connection != websocket: # Ne pas renvoyer le message à l'expéditeur (optionnel)
                    await connection.send_text(data)
                else: # Renvoyer le message à l'expéditeur pour confirmation ou affichage
                    await connection.send_text(data)

    except Exception as e:
        print(f"Erreur WebSocket pour {websocket.client}: {e}")
    finally:
        active_connections.remove(websocket)
        print(f"Connexion WebSocket fermée: {websocket.client}")
