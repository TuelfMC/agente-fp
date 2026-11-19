# Agentes de inteligencia artificial

Un agente es un programa que percibe una entrada, razona, decide una acción y observa el resultado de herramientas. Este agente combina un cerebro que genera decisiones con herramientas que realizan cálculos o consultas verificables. La separación permite cambiar el cerebro sin modificar el registro de herramientas.

El bucle razonar-actuar-observar comienza con un mensaje del usuario y termina con una respuesta final. Entre ambos estados, el agente puede ejecutar una herramienta por turno y comprobar su observación. Un agente debe limitar sus pasos y sus datos de salida para evitar bucles o resultados excesivos.

Una herramienta recibe argumentos estructurados y devuelve texto. Así, el cálculo y el acceso a datos quedan fuera del modelo. El agente no inventa resultados: usa observaciones reales antes de responder.
