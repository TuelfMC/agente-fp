# Privacidad

NetTutor trata mensajes enviados por el usuario, el identificador de chat y las respuestas del agente. La memoria SQLite guarda únicamente las últimas conversaciones necesarias en `datos/agente.sqlite3`, que no se incluye en Git.

El cerebro de reglas y los apuntes permanecen en la máquina. Ollama también procesa localmente. El cerebro API envía el contexto configurado al endpoint indicado por `API_URL`; antes de usarlo se debe revisar su política de datos. Las consultas de clima se envían a Open-Meteo solo con el nombre del lugar.

No se solicitan datos personales reales ni hay registro de pagos reales. Los chats Telegram deben usar IDs sintéticos o propios. El usuario puede escribir `/reset` para borrar el historial del chat. La carpeta `datos/` puede eliminarse manualmente para borrar toda la memoria local.
