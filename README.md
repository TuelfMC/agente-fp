# NetTutor

Agente por mensajería para estudiar redes y sistemas. Recibe mensajes por consola, Telegram o un simulador SMS, razona con una política local o un modelo compatible, usa herramientas y devuelve una respuesta final.

## Arquitectura

```text
Consola / Telegram / SMS
          |
          v
       main.py
          |
          v
    agente.py (razonar -> actuar -> observar)
       /       \
 cerebro.py  herramientas.py
       \       /
      memoria.py (SQLite)
```

## Arranque en 5 pasos

1. Instala Python 3.10 o superior.
2. Entra en `agente-fp` y ejecuta `py -m pip install -r requirements.txt`.
3. Copia `.env.example` a `.env` y configura solo lo necesario.
4. Ejecuta `py main.py --canal consola`.
5. Para Telegram configura token y allowlist; para SMS usa `--canal sms`.

## Canales

- Consola: `py main.py --canal consola`
- Telegram: `py main.py --canal telegram`
- SMS simulado: `py main.py --canal sms`

Telegram mantiene una allowlist cerrada mediante `TELEGRAM_ADMINS`. Vacía significa que nadie puede recibir respuesta. Añade chat IDs separados por comas. `TELEGRAM_TOKEN` es obligatorio.

## Cambiar cerebro

Define `CEREBRO=reglas`, `CEREBRO=ollama` o `CEREBRO=api` en `.env`.

- Ollama usa `OLLAMA_URL` y `OLLAMA_MODEL`; por defecto apunta a `llama3.2:3b`.
- API usa `API_URL`, `API_KEY` y `API_MODEL`.

## Evaluación

```text
py -m unittest tests/test_herramientas.py -v
set CEREBRO=reglas
py tests/evaluar.py
```

En PowerShell se puede usar `$env:CEREBRO="ollama"` y luego ejecutar la evaluación. Los resultados se guardan en `tests/resultados/<cerebro>.md`.

## Riesgos y contramedidas

| Riesgo | Contramedida |
|---|---|
| Acceso a datos ajenos | Datos sintéticos y memoria aislada por chat |
| Prompt injection | Instrucciones de defensa en el prompt de sistema |
| Código malicioso | Calculadora basada en AST sin llamadas ni nombres arbitrarios |
| Exponente o entrada costosa | Exponente máximo 100 y expresiones de máximo 120 caracteres |
| Respuestas demasiado largas | Truncado de herramientas y límite máximo de salida |
| Secretos expuestos | `.env` excluido por Git |
| Acceso Telegram no autorizado | Allowlist cerrada |
| Abuso por mensajes repetidos | Ventana deslizante por chat |
| Datos personales innecesarios | Solo se guarda chat sintético y texto del curso |
