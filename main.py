import argparse
import os
import time
from collections import defaultdict, deque

from dotenv import load_dotenv

import agente


VENTANAS = defaultdict(deque)
MAX_ENTRADA = 1500


def guardarrailes(chat, texto):
    ahora = time.monotonic()
    ventana = VENTANAS[chat]
    limite = int(os.getenv("MAX_MSG_MIN", "10"))
    while ventana and ahora - ventana[0] > 60:
        ventana.popleft()
    if len(ventana) >= limite:
        return "Demasiados mensajes. Espera un minuto."
    if len(texto) > MAX_ENTRADA:
        return "El mensaje excede 1500 caracteres."
    ventana.append(ahora)
    return None


def manejador(chat, texto):
    bloqueo = guardarrailes(chat, texto)
    if bloqueo:
        return bloqueo
    return agente.responder(chat, texto)


def consola():
    print("NetTutor iniciado. Escribe /reset para borrar el historial o salir para terminar.")
    chat = "consola"
    while True:
        try:
            texto = input("Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nHasta pronto.")
            return
        if texto.lower() in ("salir", "exit", "quit"):
            print("Hasta pronto.")
            return
        if not texto:
            continue
        print("NetTutor:", manejador(chat, texto))


def principal():
    load_dotenv()
    parser = argparse.ArgumentParser(description="NetTutor")
    parser.add_argument("--canal", choices=("consola", "telegram", "sms"), default="consola")
    args = parser.parse_args()
    if args.canal == "consola":
        consola()
    elif args.canal == "telegram":
        import canal_telegram
        canal_telegram.escuchar(manejador)
    else:
        import canal_sms_sim
        canal_sms_sim.escuchar(manejador)


if __name__ == "__main__":
    principal()
