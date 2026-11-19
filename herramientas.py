import ast
import datetime
import ipaddress
import re
import requests
from pathlib import Path

def _texto(resultado):
    texto = str(resultado)
    return texto[:1500]

def hora(args=None):
    try:
        ahora = datetime.datetime.now().astimezone()
        return ahora.strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception as exc:
        return f"ERROR: Hora: {exc}"

_OPERADORES = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow)

def calculadora(args):
    expresion = args.get("expresion", "") if isinstance(args, dict) else ""
    if not isinstance(expresion, str):
        return "ERROR: Calculadora: expresión inválida"
    if len(expresion) > 120:
        return "ERROR: Calculadora: expresión mayor de 120 caracteres"
    try:
        nodo = ast.parse(expresion, mode="eval")
    except (SyntaxError, ValueError) as exc:
        return f"ERROR: Sintaxis: {exc}"

    def evaluar(n):
        if isinstance(n, ast.Expression):
            return evaluar(n.body)
        if isinstance(n, ast.Constant) and type(n.value) in (int, float):
            if isinstance(n.value, float) and not abs(n.value) < float("inf"):
                raise ValueError("número no finito")
            return n.value
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.UAdd, ast.USub)):
            valor = evaluar(n.operand)
            return valor if isinstance(n.op, ast.UAdd) else -valor
        if isinstance(n, ast.BinOp) and isinstance(n.op, _OPERADORES):
            if isinstance(n.op, ast.Pow):
                for hijo in ast.walk(n):
                    if isinstance(hijo, ast.BinOp) and isinstance(hijo.op, ast.Pow):
                        try:
                            exponente = evaluar(hijo.right)
                            if isinstance(exponente, (int, float)) and abs(exponente) > 100:
                                return "ERROR: Exponente: mayor que 100"
                        except Exception:
                            pass
            izquierdo = evaluar(n.left)
            derecho = evaluar(n.right)
            if isinstance(izquierdo, str) or isinstance(derecho, str):
                return "ERROR: Tipo: operación no permitida"
            if isinstance(n.op, ast.Add): return izquierdo + derecho
            if isinstance(n.op, ast.Sub): return izquierdo - derecho
            if isinstance(n.op, ast.Mult): return izquierdo * derecho
            if isinstance(n.op, ast.Div): return izquierdo / derecho
            if isinstance(n.op, ast.FloorDiv): return izquierdo // derecho
            if isinstance(n.op, ast.Mod): return izquierdo % derecho
            if isinstance(n.op, ast.Pow): return izquierdo ** derecho
        raise ValueError("operación no permitida")

    try:
        resultado = evaluar(nodo)
        if isinstance(resultado, str):
            return resultado
        if isinstance(resultado, float) and resultado.is_integer():
            resultado = int(resultado)
        return str(resultado)
    except ZeroDivisionError:
        return "ERROR: División: división por cero"
    except Exception as exc:
        return f"ERROR: Tipo: {exc}"

def clima(args):
    lugar = args.get("lugar", "") if isinstance(args, dict) else ""
    if not isinstance(lugar, str) or not lugar.strip():
        return "ERROR: Argumentos: falta lugar"
    try:
        geo = requests.get("https://geocoding-api.open-meteo.com/v1/search",
                           params={"name": lugar, "count": 1, "language": "es", "format": "json"},
                           timeout=15)
        geo.raise_for_status()
        datos = geo.json()
        if not datos.get("results"):
            return "ERROR: Clima: lugar no encontrado"
        sitio = datos["results"][0]
        pronostico = requests.get("https://api.open-meteo.com/v1/forecast",
                                  params={"latitude": sitio["latitude"], "longitude": sitio["longitude"],
                                          "current": "temperature_2m"},
                                  timeout=15)
        pronostico.raise_for_status()
        temp = pronostico.json()["current"]["temperature_2m"]
        return f"{sitio['name']}: {temp}°C"
    except requests.RequestException as exc:
        return f"ERROR: Red: {exc}"
    except Exception as exc:
        return f"ERROR: Clima: {exc}"

def buscar_apuntes(args):
    consulta = args.get("consulta", "") if isinstance(args, dict) else ""
    palabras = [p.lower() for p in re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+", consulta) if len(p) > 3]
    if not palabras:
        return "ERROR: Argumentos: consulta sin palabras útiles"
    resultados = []
    carpeta = Path(__file__).resolve().parent / "apuntes"
    for ruta in sorted(carpeta.glob("*.md")):
        texto = ruta.read_text(encoding="utf-8")
        for parrafo in re.split(r"\n\s*\n", texto):
            parrafo = " ".join(parrafo.split())
            if len(parrafo) < 40:
                continue
            bajas = parrafo.lower()
            puntos = sum(bajas.count(palabra) for palabra in palabras)
            if puntos:
                resultados.append((puntos, parrafo[:400]))
    resultados.sort(key=lambda item: item[0], reverse=True)
    if not resultados:
        return "No se encontró información en los apuntes locales."
    return "\n\n".join(parrafo for _, parrafo in resultados[:3])

def subred(args):
    cidr = args.get("cidr", "") if isinstance(args, dict) else ""
    try:
        red = ipaddress.ip_network(cidr, strict=False)
        if red.version != 4:
            return "ERROR: Subred: solo se admite IPv4"
        utilizables = max(red.num_addresses - 2, 0)
        if red.prefixlen == 32:
            utilizables = 1
        elif red.prefixlen == 31:
            utilizables = 0
        return (f"Red: {red.network_address}; máscara: {red.netmask}; "
                f"broadcast: {red.broadcast_address}; rango: {red.network_address} - {red.broadcast_address}; "
                f"hosts utilizables: {utilizables}")
    except (ValueError, TypeError) as exc:
        return f"ERROR: Subred: {exc}"

def convertir_base(args):
    valor = args.get("valor", "") if isinstance(args, dict) else ""
    origen = args.get("base_origen")
    destino = args.get("base_destino")
    if origen not in (2, 8, 10, 16) or destino not in (2, 8, 10, 16):
        return "ERROR: Base: bases admitidas 2, 8, 10 y 16"
    try:
        numero = int(str(valor).strip(), int(origen))
        if destino == 2: salida = bin(numero)[2:]
        elif destino == 8: salida = oct(numero)[2:]
        elif destino == 10: salida = str(numero)
        else: salida = format(numero, "X")
        return salida
    except (ValueError, TypeError) as exc:
        return f"ERROR: Conversión: {exc}"

SERVICIOS = {
    "20": "FTP datos", "21": "FTP control", "22": "SSH", "23": "Telnet", "25": "SMTP",
    "53": "DNS", "67": "DHCP servidor", "68": "DHCP cliente", "69": "TFTP", "80": "HTTP",
    "110": "POP3", "123": "NTP", "143": "IMAP", "161": "SNMP", "389": "LDAP",
    "443": "HTTPS", "445": "SMB", "465": "SMTPS", "514": "Syslog", "587": "SMTP submission",
    "993": "IMAPS", "995": "POP3S", "3306": "MySQL", "3389": "RDP", "5432": "PostgreSQL"
}
NOMBRES_SERVICIO = {nombre.lower(): puerto for puerto, texto in SERVICIOS.items()
                    for nombre in re.findall(r"[A-Za-z]+", texto)}

def puerto_servicio(args):
    consulta = args.get("consulta", "") if isinstance(args, dict) else ""
    if not isinstance(consulta, str):
        return "ERROR: Puerto: consulta inválida"
    limpia = consulta.strip().lower()
    if limpia.isdigit():
        texto = SERVICIOS.get(limpia)
        return f"{limpia}: {texto}" if texto else f"Puerto {limpia}: servicio no registrado"
    nombre = re.sub(r"[^a-z]", "", limpia)
    puerto = NOMBRES_SERVICIO.get(nombre)
    if puerto:
        return f"{nombre.upper()}: puerto {puerto} ({SERVICIOS[puerto]})"
    return f"ERROR: Puerto: servicio '{consulta}' no registrado"

HERRAMIENTAS = {
    "hora": {"fn": hora, "desc": "Fecha y hora actuales.", "args": {}},
    "calculadora": {"fn": calculadora, "desc": "Aritmética segura.", "args": {"expresion": "texto"}},
    "clima": {"fn": clima, "desc": "Tiempo actual por ciudad.", "args": {"lugar": "texto"}},
    "buscar_apuntes": {"fn": buscar_apuntes, "desc": "Busca párrafos en apuntes locales.", "args": {"consulta": "texto"}},
    "subred": {"fn": subred, "desc": "Calcula una subred IPv4.", "args": {"cidr": "texto"}},
    "convertir_base": {"fn": convertir_base, "desc": "Convierte entre base 2, 8, 10 y 16.", "args": {"valor": "texto", "base_origen": "entero", "base_destino": "entero"}},
    "puerto_servicio": {"fn": puerto_servicio, "desc": "Consulta puertos y servicios.", "args": {"consulta": "texto"}},
}

def catalogo():
    partes = []
    for nombre, dato in HERRAMIENTAS.items():
        partes.append(f"{nombre}: {dato['desc']} args={dato['args']}")
    return "\n".join(partes)

def ejecutar(nombre, args):
    try:
        dato = HERRAMIENTAS.get(nombre)
        if dato is None:
            return f"ERROR: Herramienta: '{nombre}' no existe"
        if not isinstance(args, dict):
            return "ERROR: Argumentos: se esperaba un objeto"
        return _texto(dato["fn"](args))
    except Exception as exc:
        return f"ERROR: Herramienta: {exc}"
