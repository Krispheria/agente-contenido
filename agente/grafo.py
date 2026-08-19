"""Como se conectan los nodos.

Este archivo es **el flujo**, y nada mas. Se lee de arriba abajo y se entiende
el agente entero sin abrir otro sitio. Cuando en la parte 4 aparezca el
parte 4 ya no es una linea recta: despues de extraer hay una bifurcacion.
"""

from langgraph.graph import END, START, StateGraph

from .estado import Estado
from .nodos import extraer, leer_encargo, redactar


def clasificar(estado: Estado) -> Estado:
    """Deja en el estado que pide el mensaje del cliente.

    Quien decide el `tipo` es el script de la parte 4, que compara la version
    con texto libre y la de opciones cerradas. El grafo solo necesita el dato
    ya decidido: asi la arista condicional queda a la vista, que es lo que se
    ensena aqui.
    """
    return {"tipo": estado.get("tipo", "pieza_nueva")}


def elegir_rama(estado: Estado) -> str:
    """Mira el estado y devuelve la etiqueta de la rama. Esto es un router."""
    return estado["tipo"]


def corregir(estado: Estado) -> Estado:
    """Reescribe una pieza que ya existe, en vez de empezar una nueva."""
    return redactar(estado)


def construir():
    """Devuelve el grafo compilado y listo para ejecutar o dibujar."""
    grafo = StateGraph(Estado)

    # Los pasos: nombre visible -> funcion que lo hace.
    # Ese nombre es el que sale en el diagrama y el que se enciende en el panel.
    grafo.add_node("leer_encargo", leer_encargo)
    grafo.add_node("extraer", extraer)
    grafo.add_node("clasificar", clasificar)
    grafo.add_node("redactar", redactar)
    grafo.add_node("corregir", corregir)

    # Hasta clasificar, el orden es el mismo de siempre.
    grafo.add_edge(START, "leer_encargo")
    grafo.add_edge("leer_encargo", "extraer")
    grafo.add_edge("extraer", "clasificar")

    # Y aqui se abre. El mapeo declara las tres salidas antes de ejecutar: el
    # diagrama ya las conoce, y una etiqueta mal escrita se ve en vez de
    # colarse. La tercera no redacta, termina.
    grafo.add_conditional_edges(
        "clasificar",
        elegir_rama,
        {
            "pieza_nueva": "redactar",
            "correccion": "corregir",
            "no_encargo": END,
        },
    )

    grafo.add_edge("redactar", END)
    grafo.add_edge("corregir", END)

    return grafo.compile()
