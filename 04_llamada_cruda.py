"""Diapositivas 19 a 21 — La llamada cruda: mira lo que devuelve de verdad.

    uv run 04_llamada_cruda.py

Esta es **la unica vez en todo el curso que se sale del framework**, y es a
proposito. Aqui no hay agente ni grafo: hay una llamada a la API de OpenAI
escrita a mano, para ver con los ojos lo que devuelve el modelo cuando le das
herramientas.

Y lo que devuelve **no es texto y no es una ejecucion**: es un papelito que
dice "llama a esta funcion con estos argumentos". Quien la ejecuta es tu
codigo, en la linea que pone `resultado = ...`. Ese es el punto donde tu
decides — y es el mismo punto en el que en la parte 6 pediremos permiso.
"""

import json

from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console

from agente.herramientas import buscar_publicaciones_previas

load_dotenv()

consola = Console()
cliente = OpenAI()
MODELO = "gpt-5.6-luna"

# El esquema, escrito a mano una sola vez en el curso. Esto es **todo** lo que
# el modelo sabe de tu funcion: como se llama, para que sirve y que recibe.
# En la diapositiva 22 este bloque desaparece: lo genera el decorador `@tool`.
ESQUEMA = {
    "type": "function",
    "function": {
        "name": "buscar_publicaciones_previas",
        "description": (
            "Busca en el historico de DigitalSoul si ya se publico algo sobre un tema. "
            "Usala siempre antes de escribir una pieza nueva, para no repetir un angulo."
        ),
        "parameters": {
            "type": "object",
            "properties": {"tema": {"type": "string", "description": "El tema a comprobar"}},
            "required": ["tema"],
            "additionalProperties": False,
        },
    },
}

mensajes = [
    {
        "role": "user",
        "content": "Voy a escribir una pieza sobre la diferencia entre un chat y un agente. "
        "Comprueba antes si ya publicamos algo de eso.",
    }
]

# --- 1. El modelo responde. NO ejecuta nada. -------------------------------

respuesta = cliente.chat.completions.create(
    model=MODELO, messages=mensajes, tools=[ESQUEMA], reasoning_effort="none"
)
mensaje = respuesta.choices[0].message

consola.rule("Lo que devuelve el modelo")
consola.print(f"Texto de la respuesta: [bold]{mensaje.content!r}[/]")

for peticion in mensaje.tool_calls or []:
    consola.print(f"Pide llamar a: [bold magenta]{peticion.function.name}[/]")
    consola.print(f"Con argumentos: [magenta]{peticion.function.arguments}[/]")

# --- 2. Quien ejecuta eres tu ----------------------------------------------

consola.rule("Quien ejecuta eres tu")

mensajes.append(mensaje)
for peticion in mensaje.tool_calls or []:
    argumentos = json.loads(peticion.function.arguments)

    # ESTA linea es la ejecucion. El modelo no ha tocado tu disco: lo tocas tu,
    # aqui, porque has decidido hacerle caso.
    resultado = buscar_publicaciones_previas.func(**argumentos)

    consola.print(f"[dim]{resultado}[/]")
    mensajes.append(
        {"role": "tool", "tool_call_id": peticion.id, "content": resultado}
    )

# --- 3. Se lo devuelves y sigue --------------------------------------------

consola.rule("Con el resultado en la mano")

final = cliente.chat.completions.create(
    model=MODELO, messages=mensajes, tools=[ESQUEMA], reasoning_effort="none"
)
consola.print(final.choices[0].message.content)
