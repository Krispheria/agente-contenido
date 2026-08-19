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


def _version(estado: Estado, red: str) -> Estado:
    """Redacta una version y la deja en la lista comun.

    Las tres ramas devuelven la misma clave, `borradores`; el reducer del
    estado es quien las junta sin que se pisen.
    """
    return {"borradores": [f"{red}\n{redactar(estado)['pieza']}"]}


def redactar_linkedin(estado: Estado) -> Estado:
    """La version de LinkedIn."""
    return _version(estado, "LinkedIn")


def redactar_instagram(estado: Estado) -> Estado:
    """La version de Instagram."""
    return _version(estado, "Instagram")


def redactar_x(estado: Estado) -> Estado:
    """La version de X."""
    return _version(estado, "X")


def reunir(_: Estado) -> Estado:
    """El punto donde las tres ramas ya han terminado."""
    return {}


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
    grafo.add_node("redactar_linkedin", redactar_linkedin)
    grafo.add_node("redactar_instagram", redactar_instagram)
    grafo.add_node("redactar_x", redactar_x)
    grafo.add_node("reunir", reunir)

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

    # Parte 5: redactar deja de ser un solo paso y se abre en tres. Las tres
    # salen del mismo nodo, asi que LangGraph las ejecuta en el mismo
    # super-step; al volver, todas escriben en `borradores` y el reducer las
    # junta. Se ve en el panel porque un evento trae los tres nodos a la vez.
    grafo.add_edge("redactar", "redactar_linkedin")
    grafo.add_edge("redactar", "redactar_instagram")
    grafo.add_edge("redactar", "redactar_x")
    grafo.add_edge(
        ["redactar_linkedin", "redactar_instagram", "redactar_x"],
        "reunir",
    )

    grafo.add_edge("reunir", END)
    grafo.add_edge("corregir", END)

    return grafo.compile()
