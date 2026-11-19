import unicodedata


COSTE_SEGMENTO = 0.07
coste_acumulado = 0.0


def segmentos(texto):
    tiene_acentos = any(ord(c) > 127 for c in texto)
    limite = 70 if tiene_acentos else 160
    cantidad = max(1, (len(texto) + limite - 1) // limite)
    return cantidad, limite


def escuchar(manejador):
    global coste_acumulado
    print("SMS simulado. Escribe /reset o salir.")
    chat = "sms"
    while True:
        try:
            texto = input("SMS entrante: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nHasta pronto.")
            return
        if texto.lower() in ("salir", "exit", "quit"):
            print("Hasta pronto.")
            return
        if not texto:
            continue
        respuesta = manejador(chat, texto)
        cantidad, limite = segmentos(respuesta)
        coste = cantidad * COSTE_SEGMENTO
        coste_acumulado += coste
        print(f"SMS: {respuesta}")
        print(f"Segmentos: {cantidad}; límite efectivo: {limite}; coste: {coste:.2f} EUR")
        print(f"Coste acumulado: {coste_acumulado:.2f} EUR")
