import sqlite3
from pathlib import Path

RUTA = Path(__file__).resolve().parent / "datos" / "agente.sqlite3"

def guardar(chat, rol, texto):
    RUTA.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(RUTA) as conexion:
        conexion.execute("CREATE TABLE IF NOT EXISTS mensajes (id INTEGER PRIMARY KEY AUTOINCREMENT, chat TEXT, rol TEXT, texto TEXT)")
        conexion.execute("INSERT INTO mensajes(chat,rol,texto) VALUES (?,?,?)", (chat, rol, texto))
        conexion.commit()

def historial(chat, n=6):
    RUTA.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(RUTA) as conexion:
        conexion.execute("CREATE TABLE IF NOT EXISTS mensajes (id INTEGER PRIMARY KEY AUTOINCREMENT, chat TEXT, rol TEXT, texto TEXT)")
        filas = conexion.execute(
            "SELECT rol,texto FROM mensajes WHERE chat=? ORDER BY id DESC LIMIT ?", (chat, n)
        ).fetchall()
    return [{"role": rol, "content": texto} for rol, texto in reversed(filas)]

def borrar(chat):
    RUTA.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(RUTA) as conexion:
        conexion.execute("CREATE TABLE IF NOT EXISTS mensajes (id INTEGER PRIMARY KEY AUTOINCREMENT, chat TEXT, rol TEXT, texto TEXT)")
        conexion.execute("DELETE FROM mensajes WHERE chat=?", (chat,))
        conexion.commit()
