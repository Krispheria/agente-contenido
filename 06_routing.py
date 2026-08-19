"""Diapositivas 30 a 33 — Una frase no siempre sirve como clave.

    uv run 06_routing.py                 clasifica los tres mensajes cerrando opciones
    uv run 06_routing.py --texto-libre   deja que el modelo responda como una persona
    uv run 06_routing.py --estructurado  repite con el contrato `Literal`

El primer modo y `--estructurado` usan la misma salida estructurada. La
variante de texto libre existe para mostrar el fallo: no promete que ocurra en
cada llamada, porque el modelo puede acertar una clave por casualidad.
"""

import argparse
import json
import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from rich.console import Console

from agente.nodos import MODELO_MECANICO, _modelo

MENSAJES = Path(__file__).resolve().parent / "mensajes-cliente.json"
RUTAS = {
    "pieza_nueva": "pieza_nueva",
    "correccion": "correccion",
    "no_encargo": "END",
}
consola = Console()


class Clasificacion(BaseModel):
    """El contrato que convierte una decisión del modelo en una clave usable."""

    tipo: Literal["pieza_nueva", "correccion", "no_encargo"] = Field(
        description="Qué está pidiendo el cliente en este mensaje"
    )


def cargar_mensajes() -> list[dict[str, str]]:
    """Lee los casos fijos para repetir la demo sin cambiar la entrada."""
    return json.loads(MENSAJES.read_text(encoding="utf-8"))


def comprobar_clave() -> None:
    """Evita una traza de la librería cuando falta la configuración inicial."""
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        consola.print(
            "[red]Falta OPENAI_API_KEY.[/] Copia .env.example a .env y añade tu clave."
        )
        raise SystemExit(1)


def clasificar_estructurado(mensaje: str) -> str:
    """Pide una de las tres claves que el grafo sí sabe enrutar."""
    modelo = _modelo(MODELO_MECANICO).with_structured_output(Clasificacion)
    datos = modelo.invoke(mensaje)
    return datos.tipo


def mostrar_ruta(caso: str, mensaje: str, tipo: str) -> None:
    """Deja a la vista la clasificación y la rama que activa."""
    consola.rule(caso.replace("_", " ").title())
    consola.print(f"[dim]{mensaje}[/]")
    consola.print(f"tipo: [bold]{tipo}[/]  →  {RUTAS[tipo]}")


def ejecutar_estructurado() -> None:
    """Clasifica los tres casos que sí tienen una rama definida."""
    for entrada in cargar_mensajes()[:3]:
        tipo = clasificar_estructurado(entrada["mensaje"])
        mostrar_ruta(entrada["caso"], entrada["mensaje"], tipo)


def ejecutar_texto_libre() -> None:
    """Muestra por qué una respuesta humana no es un identificador del programa."""
    entrada = cargar_mensajes()[3]
    modelo = _modelo(MODELO_MECANICO)
    respuesta = modelo.invoke(
        "Clasifica este mensaje como pieza nueva, corrección o no encargo. "
        "Explica brevemente tu decisión.\n\n"
        f"{entrada['mensaje']}"
    )
    texto = respuesta.content.strip()

    consola.rule("La respuesta en texto libre")
    consola.print(f"[dim]{texto}[/]")
    try:
        consola.print(f"Ruta: {RUTAS[texto]}")
    except KeyError:
        consola.print(
            "[red]No hay una ruta para esa frase:[/] el programa esperaba una clave exacta."
        )


def argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Demuestra las dos formas de enrutar.")
    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument("--texto-libre", action="store_true")
    grupo.add_argument("--estructurado", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    opciones = argumentos()
    comprobar_clave()
    if opciones.texto_libre:
        ejecutar_texto_libre()
    else:
        ejecutar_estructurado()
