"""Lo que viaja por el grafo.

Un unico sitio donde mirar para saber que datos existen. Cada nodo lee de aqui
y devuelve **solo los campos que cambia**, no el estado entero.

`total=False` significa que ninguno es obligatorio al arrancar: van
apareciendo segun los nodos los rellenan.
"""

from operator import add
from typing import Annotated, TypedDict


class Estado(TypedDict, total=False):
    encargo: str
    """El texto suelto que entra. Lo carga el nodo `leer_encargo`."""

    temas: list[str]
    """Los temas que el modelo saco del encargo."""

    tono: str
    """El tono pedido, en dos o tres palabras."""

    pieza: str
    """El texto redactado. Es la salida del agente."""

    tipo: str
    """Que pide el mensaje del cliente: pieza nueva, correccion o ninguna.

    Lo rellena el clasificador y lo lee la arista condicional para elegir rama."""

    borradores: Annotated[list[str], add]
    """Las versiones que devuelven las ramas del abanico.

    Lleva reducer porque tres nodos escriben esta clave a la vez: `add` las
    acumula en una lista en vez de pisarse. Sin el, seria un conflicto."""
