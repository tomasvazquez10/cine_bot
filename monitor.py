import os
import requests
from bs4 import BeautifulSoup
from flask import Flask

app = Flask(__name__)

URL = "https://entradas.todoshowcase.com/showcase/pelicula.aspx?filmid=5875"
FECHA_ISO_OBJETIVO = "2026-08-06"
FECHA_TEXTO_OBJETIVO = "6/08"

# Se leen directamente de las Variables de Entorno de Render
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

def enviar_telegram(mensaje):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Error: No se configuraron TELEGRAM_TOKEN o TELEGRAM_CHAT_ID.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensaje,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"Error enviando a Telegram: {e}")

def chequear_cine():
    try:
        session = requests.Session()
        res = session.get(URL, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        botones = soup.select("button.op_day")
        encontrado = any(
            FECHA_ISO_OBJETIVO in b.get("value", "") or FECHA_TEXTO_OBJETIVO in b.text 
            for b in botones
        )
        
        if not encontrado and (FECHA_ISO_OBJETIVO in res.text or FECHA_TEXTO_OBJETIVO in res.text):
            encontrado = True

        if encontrado:
            msg = f"<b>¡ENTRADAS HABILITADAS!</b>\nSe detectó el <b>Jue {FECHA_TEXTO_OBJETIVO}</b>.\n\nComprá acá: {URL}"
            enviar_telegram(msg)
            return f"¡Entradas encontradas! Notificación enviada para el {FECHA_TEXTO_OBJETIVO}."
        
        return f"Revisión realizada a las {res.headers.get('Date', '')}: Aún no están las entradas para el {FECHA_TEXTO_OBJETIVO}."
    except Exception as e:
        return f"Error revisando el cine: {e}"

@app.route("/")
def home():
    resultado = chequear_cine()
    return f"Status Bot: OK.<br>{resultado}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
