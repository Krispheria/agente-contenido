"""Las herramientas del agente. Parte 3 del curso.

De cada funcion, el modelo ve **tres cosas**: el nombre, el docstring y los
tipos de los parametros. El cuerpo no lo ve nunca. Por eso el docstring no es
un comentario para el companero de al lado: **es la interfaz con el modelo**.

Cada docstring de aqui tiene tres partes deliberadas, y se explican una a una:

    1. Que hace.
    2. Cuando usarla.
    3. **Cuando NO usarla** — la que casi nadie escribe y la que mas cambia
       el comportamiento.

Al final del archivo estan las dos mismas herramientas con la descripcion que
escribe todo el mundo la primera vez ("busca informacion", "consulta datos").
Sirven para la demo de la diapositiva 23: mismas funciones, mismo modelo, misma
pregunta — y el agente elige distinto. Lo unico que cambia es el texto.
"""

import json
from pathlib import Path

from langchain.tools import tool

HISTORICO = Path(__file__).resolve().parent.parent / "historico-publicaciones.json"

# Limites de caracteres por red, leidos el 2026-08-10. Caducan, como los precios.
LIMITES = {
    "linkedin": 3000,
    "instagram": 2200,
    "x": 280,
}


def _leer_historico() -> list[dict]:
    return json.loads(HISTORICO.read_text(encoding="utf-8"))


# --- las buenas ------------------------------------------------------------


@tool
def buscar_publicaciones_previas(tema: str) -> str:
    """Busca en el historico de DigitalSoul si ya se publico algo sobre un tema.

    Usala SIEMPRE antes de escribir una pieza nueva, para no repetir un angulo
    que ya se uso. Devuelve la fecha, la red, el angulo y como funciono.

    NO la uses para consultar limites de caracteres ni normas de una red: para
    eso esta `limites_de_plataforma`.
    """
    palabras = {p for p in tema.lower().split() if len(p) > 3}
    encontradas = [
        pub
        for pub in _leer_historico()
        if palabras & {p for p in pub["tema"].lower().split() if len(p) > 3}
    ]
    if not encontradas:
        return f"No hay nada publicado sobre '{tema}'. Angulo libre."
    return "\n".join(
        f"{p['fecha']} · {p['red']} · angulo usado: \"{p['angulo']}\" ({p['rendimiento']})"
        for p in encontradas
    )


@tool
def limites_de_plataforma(red: str) -> str:
    """Devuelve el limite de caracteres de una red social concreta.

    Usala cuando tengas que ajustar una pieza al formato de una red. Acepta
    'linkedin', 'instagram' o 'x'.

    NO la uses para saber que se publico antes: para eso esta
    `buscar_publicaciones_previas`.
    """
    clave = red.lower().strip()
    if clave not in LIMITES:
        # Revienta a proposito (diapositiva 25). Sin middleware, esta excepcion
        # se lleva por delante al agente entero.
        raise ValueError(
            f"No tengo los limites de '{red}'. Redes que conozco: {', '.join(LIMITES)}."
        )
    return f"{clave}: {LIMITES[clave]} caracteres por publicacion (dato del 2026-08-10)."


BUENAS = [buscar_publicaciones_previas, limites_de_plataforma]


# --- las mismas, con el docstring que escribe todo el mundo -----------------
#
# Mismo nombre de herramienta, mismo codigo, mismos tipos. Solo cambia el texto
# que lee el modelo. El nombre de la funcion de Python tiene que ser distinto
# porque conviven en el mismo archivo; el nombre que ve el modelo se fija en el
# decorador y es identico al de arriba.


@tool("buscar_publicaciones_previas")
def _buscar_vaga(tema: str) -> str:
    """Busca informacion."""
    return buscar_publicaciones_previas.func(tema)


@tool("limites_de_plataforma")
def _limites_vaga(red: str) -> str:
    """Consulta datos."""
    return limites_de_plataforma.func(red)


VAGAS = [_buscar_vaga, _limites_vaga]


# --- y las mismas otra vez, sin nombre que las salve -----------------------
#
# Medido el 2026-08-14: con los nombres de arriba el agente acierta igual aunque
# la descripcion sea mala, porque `limites_de_plataforma` ya dice a que viene.
# **El nombre tambien es interfaz.** Cuando se apaga tambien esa pista, el
# modelo se queda solo con "busca informacion" y "consulta datos" — y a partir
# de ahi elige a ciegas.


@tool("consultar_datos")
def _opaca_historico(tema: str) -> str:
    """Consulta datos."""
    return buscar_publicaciones_previas.func(tema)


@tool("buscar_info")
def _opaca_limites(red: str) -> str:
    """Busca informacion."""
    return limites_de_plataforma.func(red)


OPACAS = [_opaca_historico, _opaca_limites]


# --- el arreglo: mismos nombres malos, docstring bien escrito --------------
#
# No se toca el nombre a proposito. Sirve para ensenar que **el docstring
# rescata un nombre malo**: es el arreglo mas barato que existe, y se hace en
# directo delante de la clase.


@tool("consultar_datos")
def _rescatada_historico(tema: str) -> str:
    """Busca en el historico de DigitalSoul si ya se publico algo sobre un tema.

    Usala antes de escribir una pieza nueva, para no repetir un angulo.

    NO la uses para limites de caracteres ni normas de una red.
    """
    return buscar_publicaciones_previas.func(tema)


@tool("buscar_info")
def _rescatada_limites(red: str) -> str:
    """Devuelve el limite de caracteres de una red social ('linkedin', 'instagram', 'x').

    Usala cuando haya que ajustar una pieza al formato de una red.

    NO la uses para saber que se publico antes.
    """
    return limites_de_plataforma.func(red)


RESCATADAS = [_rescatada_historico, _rescatada_limites]
