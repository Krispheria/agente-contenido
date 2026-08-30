"""Tools 2 — Dos herramientas, y el agente elige la que toca.

    uv run 06_dos_tools.py                                   pregunta de red    -> tool interna
    uv run 06_dos_tools.py "Dame contexto sobre <un tema>"   documentarse       -> Wikipedia

Una herramienta es codigo tuyo (un diccionario en `agente/herramientas_demo.py`);
la otra sale a internet (la API publica de Wikipedia, sin key). El agente no
distingue "interna" de "externa": ve dos fichas —nombre, docstring, tipos— y
elige por lo que dicen. Cambia la pregunta y cambia la mano que levanta.
"""

import sys

from langchain.agents import create_agent
from langchain_core.callbacks import get_usage_metadata_callback
from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI
from rich.console import Console

from agente.herramientas_demo import DEMO
from agente.nodos import MODELO_MECANICO
from agente.precios import FECHA_PRECIOS, coste

consola = Console()

PREGUNTA_DEFECTO = "Voy a publicar en Instagram. Cuantos caracteres tengo?"

# La pregunta se pasa como argumento; sin argumento, la de la red social.
pregunta = " ".join(sys.argv[1:]).strip() or PREGUNTA_DEFECTO

INSTRUCCIONES = (
    "Eres el asistente de contenido de DigitalSoul. Antes de proponer nada, "
    "usa las herramientas que tienes. No inventes datos que puedas consultar."
)

# `reasoning_effort="none"`: con este modelo, /v1/chat/completions rechaza las
# herramientas si el razonamiento esta encendido (el muro de la parte de tools).
modelo = ChatOpenAI(model=MODELO_MECANICO, temperature=0, reasoning_effort="none")

agente = create_agent(model=modelo, tools=DEMO, system_prompt=INSTRUCCIONES)

consola.rule("Dos tools: una interna, una externa")
consola.print(f"[dim]{pregunta}[/]\n")

with get_usage_metadata_callback() as uso:
    resultado = agente.invoke({"messages": [{"role": "user", "content": pregunta}]})

# El historial es append-only: se lee de arriba abajo como una conversacion.
for mensaje in resultado["messages"]:
    for peticion in getattr(mensaje, "tool_calls", None) or []:
        consola.print(
            f"[bold magenta]PIDE[/] {peticion['name']}  [dim]{peticion['args']}[/]"
        )
    if isinstance(mensaje, ToolMessage):
        primera = mensaje.content.split("\n")[0]
        consola.print(f"[bold green]DEVUELVE[/] [dim]{primera}[/]")

consola.rule("La respuesta final")
consola.print(resultado["messages"][-1].content)

consola.print(
    f"\n[dim]Coste: ${coste(uso.usage_metadata):.6f} "
    f"(precios del {FECHA_PRECIOS})[/]"
)
