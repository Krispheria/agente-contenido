"""Diapositiva 13 — Diez lineas y ya ves por donde va.

    uv run 02_traza.py

Ejecuta el agente **de verdad**, con sus llamadas a la API, y va escribiendo
que nodo acaba de terminar segun termina. No es un log que sale al final: se
escribe mientras pasa.

El mecanismo entero cabe en una frase: `stream(stream_mode="updates")` va
soltando un diccionario `{nombre_del_nodo: lo_que_cambio}` cada vez que un paso
acaba. Con eso se puede pintar lo que quieras — aqui la terminal, en la
diapositiva 14 un diagrama que se enciende.

Esta es la version que **nunca falla**: no necesita navegador. Si el panel se
rompe en directo, la clase sigue por aqui.
"""

from langchain_core.callbacks import get_usage_metadata_callback
from rich.console import Console

from agente.grafo import construir
from agente.precios import FECHA_PRECIOS, coste

consola = Console()
grafo = construir()

consola.rule("El agente arranca")

# El bucle. Esto es todo: por cada paso que termina, quien fue y que cambio.
# El `with` de alrededor va sumando los tokens de todas las llamadas del run, y
# se puede **mirar por el camino**: al acabar cada paso ya lleva contadas sus
# llamadas. De esa resta sale lo que costo ese paso.
gastado = 0.0

with get_usage_metadata_callback() as uso:
    for paso in grafo.stream({}, stream_mode="updates"):
        acumulado = coste(uso.usage_metadata)
        ahora = acumulado - gastado
        gastado = acumulado

        for nodo, cambios in paso.items():
            consola.print(f"[bold green]OK[/] [bold]{nodo}[/]")
            for campo, valor in cambios.items():
                resumen = str(valor).replace("\n", " ")
                if len(resumen) > 100:
                    resumen = resumen[:100] + "..."
                consola.print(f"     {campo}: [dim]{resumen}[/]")

        etiqueta = f"+${ahora:.6f}" if ahora else "gratis, no llamo al modelo"
        consola.print(f"     [magenta]{etiqueta}[/] [dim]· total ${acumulado:.6f}[/]")

consola.rule("La factura")

for modelo, tokens in uso.usage_metadata.items():
    consola.print(
        f"{modelo}: {tokens.get('input_tokens', 0)} de entrada, "
        f"{tokens.get('output_tokens', 0)} de salida"
    )

consola.print(
    f"[bold]Coste: ${coste(uso.usage_metadata):.6f}[/] "
    f"[dim](precios del {FECHA_PRECIOS}; si cambian, cambia el numero)[/]"
)
