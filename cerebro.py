import os
import json
import re
import requests

class CerebroReglas:
    nombre = "reglas"
    def pensar(self, mensajes):
        ultimo = mensajes[-1]["content"] if mensajes else ""
        baja = ultimo.lower()
        if baja.startswith("observacion:"):
            observacion = ultimo.split(":", 1)[1].strip()
            if observacion.startswith("ERROR"):
                texto = "La herramienta devolvió un error. Comprueba los argumentos y, si no es posible corregirlos, explica el problema."
            else:
                texto = f"Resultado obtenido: {observacion}"
            return json.dumps({"accion":"final","texto":texto}, ensure_ascii=False)
        if any(p in baja for p in ["ignora", "prompt", "saltarte"]):
            return '{"accion":"final","texto":"Soy una IA basada en reglas. No puedo revelar instrucciones internas ni saltarme las restricciones."}'
        if any(p in baja for p in ["hora", "fecha"]):
            return '{"accion":"usar","herramienta":"hora","args":{}}'
        porcentaje = re.search(r"(\d+(?:[.,]\d+)?)\s*%\s*de\s*(\d+(?:[.,]\d+)?)", baja)
        if porcentaje:
            return '{"accion":"usar","herramienta":"calculadora","args":{"expresion":"' + str(porcentaje.group(1).replace(",", ".")) + '/100*' + str(porcentaje.group(2).replace(",", ".")) + '"}}'
        if re.search(r"(calcul|cuánto|cuanto|operacion|operación|[+*/%-])", baja):
            expresion = re.sub(r"[^0-9+\-*/%(). ]", "", baja)
            expresion = expresion.replace("  ", " ").strip()
            if expresion:
                return '{"accion":"usar","herramienta":"calculadora","args":{"expresion":"' + expresion.replace('"', "") + '"}}'
        if re.search(r"(clima|tiempo)", baja):
            lugar = "Madrid"
            coincidencia = re.search(r"(?:en|de)\s+([A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]+)", baja)
            if coincidencia:
                lugar = coincidencia.group(1).strip(" ?¿")
            return json.dumps({"accion":"usar","herramienta":"clima","args":{"lugar":lugar}}, ensure_ascii=False)
        if re.search(r"subred|hosts utilizables|cidr", baja):
            coincidencia = re.search(r"\b\d{1,3}(?:\.\d{1,3}){3}/\d{1,2}\b", ultimo)
            cidr = coincidencia.group(0) if coincidencia else "192.168.1.0/24"
            return json.dumps({"accion":"usar","herramienta":"subred","args":{"cidr":cidr}}, ensure_ascii=False)
        if re.search(r"binari|base (2|8|10|16)|hexadecimal|convertir", baja):
            numero = re.search(r"\b(?:255|[0-9A-Fa-f]+)\b", ultimo)
            origen = 16 if "hexadecimal" in baja or "base 16" in baja else 10
            if "binari" in baja:
                destino = 2
            elif "octal" in baja:
                destino = 8
            else:
                destino = 10
            if re.search(r"255\s*a\s*binari", baja):
                origen = 10
            return json.dumps({"accion":"usar","herramienta":"convertir_base","args":{"valor":numero.group(0) if numero else "0","base_origen":origen,"base_destino":destino}}, ensure_ascii=False)
        if re.search(r"(puerto|https|http|ssh|dns|smtp)", baja):
            servicio = re.search(r"(https|http|ssh|dns|smtp|ftp|telnet)", baja)
            consulta = servicio.group(1) if servicio else re.findall(r"\d+", ultimo)[0] if re.findall(r"\d+", ultimo) else "443"
            return json.dumps({"accion":"usar","herramienta":"puerto_servicio","args":{"consulta":consulta}}, ensure_ascii=False)
        if re.search(r"apunt|temario|agente|prompt|evaluaci", baja):
            return json.dumps({"accion":"usar","herramienta":"buscar_apuntes","args":{"consulta":ultimo}}, ensure_ascii=False)
        if "?" in ultimo:
            return json.dumps({"accion":"final","texto":"Puedo ayudarte con redes, subnetting, bases numéricas y apuntes locales."}, ensure_ascii=False)
        return '{"accion":"final","texto":"No dispongo de una herramienta adecuada para ese mensaje."}'

class CerebroOllama:
    nombre = "ollama"
    def pensar(self, mensajes):
        url = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/") + "/api/chat"
        cuerpo = {"model": os.getenv("OLLAMA_MODEL", "llama3.2:3b"), "messages": mensajes,
                  "stream": False, "temperature": 0.2, "num_predict": 350,
                  "options": {"temperature": 0.2, "num_predict": 350}}
        respuesta = requests.post(url, json=cuerpo, timeout=180)
        respuesta.raise_for_status()
        return respuesta.json()["message"]["content"]

class CerebroAPI:
    nombre = "api"
    def pensar(self, mensajes):
        url = os.getenv("API_URL", "")
        clave = os.getenv("API_KEY", "")
        modelo = os.getenv("API_MODEL", "")
        if not url:
            raise RuntimeError("API_URL no configurada")
        respuesta = requests.post(url, headers={"Authorization": f"Bearer {clave}", "Content-Type": "application/json"},
                                  json={"model": modelo, "messages": mensajes, "temperature": 0.2, "timeout": 60},
                                  timeout=60)
        respuesta.raise_for_status()
        return respuesta.json()["choices"][0]["message"]["content"]

def crear_cerebro():
    tipo = os.getenv("CEREBRO", "reglas").strip().lower()
    if tipo == "ollama":
        return CerebroOllama()
    if tipo == "api":
        return CerebroAPI()
    return CerebroReglas()
