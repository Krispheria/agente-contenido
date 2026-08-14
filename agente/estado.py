"""Lo que viaja por el grafo.

Un unico sitio donde mirar para saber que datos existen. Cada nodo lee de aqui
y devuelve **solo los campos que cambia**, no el estado entero.

`total=False` significa que ninguno es obligatorio al arrancar: van
apareciendo segun los nodos los rellenan.
"""

from typing import TypedDict


class Estado(TypedDict, total=False):
    encargo: str
    """El texto suelto que entra. Lo carga el nodo `leer_encargo`."""

    temas: list[str]
    """Los temas que el modelo saco del encargo."""

    tono: str
    """El tono pedido, en dos o tres palabras."""

    pieza: str
    """El texto redactado. Es la salida del agente."""
