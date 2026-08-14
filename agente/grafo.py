"""Como se conectan los nodos.

Este archivo es **el flujo**, y nada mas. Se lee de arriba abajo y se entiende
el agente entero sin abrir otro sitio. Cuando en la parte 4 aparezca el
routing, la bifurcacion se vera aqui.
"""

from langgraph.graph import END, START, StateGraph

from .estado import Estado
from .nodos import extraer, leer_encargo, redactar


def construir():
    """Devuelve el grafo compilado y listo para ejecutar o dibujar."""
    grafo = StateGraph(Estado)

    # Los pasos: nombre visible -> funcion que lo hace.
    # Ese nombre es el que sale en el diagrama y el que se enciende en el panel.
    grafo.add_node("leer_encargo", leer_encargo)
    grafo.add_node("extraer", extraer)
    grafo.add_node("redactar", redactar)

    # El orden. Por ahora una linea recta; en la parte 4 se abre.
    grafo.add_edge(START, "leer_encargo")
    grafo.add_edge("leer_encargo", "extraer")
    grafo.add_edge("extraer", "redactar")
    grafo.add_edge("redactar", END)

    return grafo.compile()
