"""Diapositiva 10 — Lo ejecutas y solo ves el resultado.

    uv run 00_ejecutar.py

La caja negra. Llama al agente, espera, y escribe la pieza. Ya esta.

Y ese es justo el problema que abre la parte 2: salio algo correcto y no
sabes por donde paso, ni cuanto tardo, ni que te costo. Todo lo que viene
despues —el diagrama, la traza y el panel— existe para responder eso.

`invoke` es esperar al final. `stream`, que es lo de la diapositiva 13, es
enterarse mientras pasa. Misma ejecucion, dos formas de mirarla.
"""

from agente.grafo import construir

grafo = construir()

resultado = grafo.invoke({})

print(resultado["pieza"])
