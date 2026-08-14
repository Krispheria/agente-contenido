"""Diapositivas 22 a 26 — El agente con herramientas.

    uv run 05_tools.py             las herramientas con su descripcion buena
    uv run 05_tools.py --vagas     las mismas, con la descripcion que escribe
                                   todo el mundo la primera vez  (dia. 23)
    uv run 05_tools.py --revienta  se le pide una red que la tool no conoce,
                                   y la excepcion no mata al agente  (dia. 25)

Todo lo que en `04_llamada_cruda.py` habia que escribir a mano —el esquema, el
bucle, el mensaje de vuelta— lo pone aqui `create_agent`. Por eso el crudo va
antes: si no, esto es magia.

Lo unico que cambia entre la ejecucion normal y `--vagas` es **el texto del
docstring**. Mismo modelo, misma pregunta, mismas funciones.
"""

import sys

from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain_core.callbacks import get_usage_metadata_callback
from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI
from rich.console import Console

from agente.herramientas import BUENAS, OPACAS, RESCATADAS, VAGAS
from agente.nodos import MODELO_MECANICO
from agente.precios import FECHA_PRECIOS, coste

consola = Console()

VAGAS_ACTIVAS = "--vagas" in sys.argv
REVIENTA = "--revienta" in sys.argv

ENCARGO_TOOLS = (
    "Voy a escribir una pieza sobre la diferencia entre un chat y un agente. "
    "Comprueba si ya publicamos algo de eso y dime que angulo evitar."
)
ENCARGO_REVIENTA = (
    "Voy a publicar la pieza en TikTok. Dime el limite de caracteres que tengo."
)
# Esta pregunta **solo** la puede responder `limites_de_plataforma`. Con las
# descripciones buenas la eleccion es evidente; con las vagas, las dos suenan
# igual de plausibles y ahi es donde se ve el efecto del docstring.
ENCARGO_LIMITE = "Voy a publicar en LinkedIn. Cuantos caracteres tengo?"

INSTRUCCIONES = (
    "Eres el asistente de contenido de DigitalSoul. Antes de proponer nada, "
    "usa las herramientas que tienes. No inventes datos que puedas consultar."
)


# El agente no se muere porque una funcion tuya lance una excepcion: se le
# devuelve el fallo **como un mensaje mas**, y el modelo decide que hacer con
# el. Sin esto, una tool rota se lleva por delante la ejecucion entera.
@wrap_tool_call
def no_te_mueras(request, handler):
    try:
        return handler(request)
    except Exception as error:
        consola.print(f"[red]La tool ha lanzado:[/] {type(error).__name__}: {error}")
        return ToolMessage(
            content=f"La herramienta ha fallado: {error}",
            tool_call_id=request.tool_call["id"],
        )


if "--rescatadas" in sys.argv:
    herramientas = RESCATADAS
elif "--opacas" in sys.argv:
    herramientas = OPACAS
elif VAGAS_ACTIVAS:
    herramientas = VAGAS
else:
    herramientas = BUENAS
if REVIENTA:
    pregunta = ENCARGO_REVIENTA
elif "--limite" in sys.argv:
    pregunta = ENCARGO_LIMITE
else:
    pregunta = ENCARGO_TOOLS

# `reasoning_effort="none"` no es un capricho de estilo: **con este modelo, la
# API rechaza las herramientas si el razonamiento esta encendido** en
# /v1/chat/completions. El error lo dice con todas las letras y la salida esta
# en 03-comandos.md. Elegir una herramienta de una lista de dos es una tarea
# mecanica: no necesita razonamiento, y asi ademas es mas barato y mas rapido.
modelo = ChatOpenAI(model=MODELO_MECANICO, temperature=0, reasoning_effort="none")

agente = create_agent(
    model=modelo,
    tools=herramientas,
    system_prompt=INSTRUCCIONES,
    middleware=[no_te_mueras],
)

consola.rule(
    f"Descripciones {'VAGAS' if VAGAS_ACTIVAS else 'buenas'}"
    f"{' · pidiendo una red desconocida' if REVIENTA else ''}"
)
consola.print(f"[dim]{pregunta}[/]\n")

with get_usage_metadata_callback() as uso:
    resultado = agente.invoke({"messages": [{"role": "user", "content": pregunta}]})

# El historial es append-only: cada turno anade mensajes, nunca los reemplaza.
# Por eso se lee de arriba abajo como una conversacion.
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
