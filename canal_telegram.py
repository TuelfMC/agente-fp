import os
import time
import requests


def _permitidos():
    texto = os.getenv("TELEGRAM_ADMINS", "").strip()
    if not texto:
        return set()
    return {parte.strip() for parte in texto.split(",") if parte.strip()}


def _post(url, parametros, intentos=3):
    for intento in range(intentos):
        try:
            respuesta = requests.post(url, json=parametros, timeout=30)
            respuesta.raise_for_status()
            return respuesta
        except requests.RequestException:
            if intento == intentos - 1:
                raise
            time.sleep(2 ** intento)


def _enviar(token, chat_id, texto):
    for inicio in range(0, len(texto), 4000):
        _post(f"https://api.telegram.org/bot{token}/sendMessage",
              {"chat_id": chat_id, "text": texto[inicio:inicio + 4000]})


def escuchar(manejador):
    token = os.getenv("TELEGRAM_TOKEN", "").strip()
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN no está configurado")
    base = f"https://api.telegram.org/bot{token}"
    try:
        _post(base + "/deleteWebhook", {"drop_pending_updates": True})
    except requests.RequestException as exc:
        print(f"ERROR Telegram al borrar webhook: {exc}")
    offset = 0
    permitidos = _permitidos()
    print("Telegram iniciado. La allowlist está vacía; nadie está autorizado." if not permitidos else
          f"Telegram iniciado. Chats autorizados: {', '.join(sorted(permitidos))}")
    while True:
        try:
            respuesta = _post(base + "/getUpdates", {"offset": offset, "timeout": 30}, intentos=3)
            for actualizacion in respuesta.json().get("result", []):
                offset = max(offset, actualizacion["update_id"] + 1)
                mensaje = actualizacion.get("message") or {}
                chat = mensaje.get("chat", {})
                chat_id = str(chat.get("id", ""))
                texto = mensaje.get("text", "")
                if chat_id not in permitidos:
                    print(f"BLOQUEADO chat_id={chat_id}")
                    continue
                if texto:
                    respuesta_agente = manejador(chat_id, texto)
                    _enviar(token, chat_id, respuesta_agente)
        except requests.RequestException as exc:
            print(f"ERROR Telegram: {exc}; reintentando")
            time.sleep(3)
