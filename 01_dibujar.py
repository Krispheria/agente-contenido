"""Diapositiva 12 — Tu grafo sabe dibujarse solo.

    uv run 01_dibujar.py

Saca el mapa del flujo: los pasos y el orden en que van. Es la estructura, no
la ejecucion — para verlo moverse esta `02_traza.py`, que es la siguiente.

Los dos juntos son el panel de la diapositiva 14: la forma sale de aqui y las
luces salen de la traza.

Cuidado con `draw_mermaid_png()`, que es la funcion que todo el mundo busca:
esa **sale a internet** (usa un servicio externo para generar la imagen). La de
aqui, `draw_mermaid()`, es texto puro y local. Para grabar, siempre esta.
"""

from agente.grafo import construir

grafo = construir()

print(grafo.get_graph().draw_mermaid())
