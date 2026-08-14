"""Los nodos del grafo: una funcion por paso.

Cada una recibe el estado y devuelve un diccionario con **lo que cambia**.
Nada mas. Si una funcion crece hasta no caber en una pantalla, es que esta
haciendo dos pasos y hay que partirla en dos nodos.
"""

from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from .estado import Estado

# Lee el .env y mete OPENAI_API_KEY en el entorno del proceso.
# Sin esta linea, la clave no llega a ninguna parte por mucho que exista el archivo.
load_dotenv()

# Precios por millon de tokens (entrada / cacheada / salida), leidos el 2026-08-10.
# Fuente: investigacion/04-paralelo-limites-coste.md. Caducan: se reverifican antes de grabar.
#
#   gpt-5.6-luna    $0.20  /  $0.02  /  $1.20     <- el barato
#   gpt-5.6-terra   $2.00  /  $0.20  /  $12.00    <- diez veces mas caro
#   gpt-5.6-sol     $5.00  /  $0.50  /  $30.00
#
# Todo el curso corre con el barato. `luna` hace de sobra lo mecanico (extraer,
# clasificar, enrutar) y redacta suficientemente bien para una demo. Subir a
# `terra` es cambiar UNA linea, y en la parte 4 se mide lo que cuesta cada uno.
MODELO_MECANICO = "gpt-5.6-luna"
MODELO_REDACCION = "gpt-5.6-luna"

# Tope de la respuesta. No es solo por la factura: OpenAI cuenta contra tu limite
# por minuto **el mayor** entre este numero y los tokens que le mandas. Ponerlo a
# 4000 "por si acaso" te gasta 4000 aunque la respuesta ocupe 200.
MAX_TOKENS_REDACCION = 400

ENCARGO = Path(__file__).resolve().parent.parent / "encargo.md"


def _modelo(nombre: str, max_tokens: int | None = None) -> ChatOpenAI:
    """Crea el cliente del modelo.

    Se crea aqui dentro y no al importar el modulo **a proposito**: asi
    `01_dibujar.py` puede dibujar el grafo sin tener API key. Dibujar es mirar
    la estructura, no ejecutarla.
    """
    return ChatOpenAI(model=nombre, temperature=0, max_tokens=max_tokens)


class Extraccion(BaseModel):
    """La forma exacta que tiene que devolver el modelo.

    Estas descripciones no son comentarios: **el modelo las lee**. Es el mismo
    mecanismo que en la parte 3 con los docstrings de las tools.
    """

    temas: list[str] = Field(description="Los temas a cubrir este mes, uno por elemento")
    tono: str = Field(description="El tono pedido, en dos o tres palabras")


def leer_encargo(estado: Estado) -> Estado:
    """Carga el encargo del mes desde el disco. Sin modelo, sin coste."""
    return {"encargo": ENCARGO.read_text(encoding="utf-8")}


def extraer(estado: Estado) -> Estado:
    """Texto suelto -> datos estructurados.

    `with_structured_output` obliga al modelo a devolver la forma de
    `Extraccion` en vez de un parrafo. Es la diferencia entre un dato con el
    que se puede trabajar y una frase que hay que interpretar.
    """
    modelo = _modelo(MODELO_MECANICO).with_structured_output(Extraccion)
    datos = modelo.invoke(
        "Este es el encargo de contenido de un mes. Saca los temas y el tono.\n\n"
        f"{estado['encargo']}"
    )
    return {"temas": datos.temas, "tono": datos.tono}


def redactar(estado: Estado) -> Estado:
    """Escribe una pieza a partir de lo que se extrajo."""
    modelo = _modelo(MODELO_REDACCION, max_tokens=MAX_TOKENS_REDACCION)
    respuesta = modelo.invoke(
        f"Escribe un post corto sobre: {estado['temas'][0]}.\n"
        f"Tono: {estado['tono']}."
    )
    return {"pieza": respuesta.content}
