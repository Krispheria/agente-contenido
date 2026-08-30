"""Las dos herramientas de la demo final de tools: una interna y una externa.

La pareja esta elegida para que la eleccion se vea de lejos: una vive en tu
codigo y la otra sale a internet, y sus dominios no se pisan. El modelo no
sabe cual es cual — ve dos fichas (nombre, docstring, tipos) y elige por lo
que dicen, igual que en `herramientas.py`.
"""

import json
import urllib.parse
import urllib.request

from langchain.tools import tool

# La misma tabla de `herramientas.py`, sin el caso que revienta: esta demo va
# de eleccion, no de errores.
LIMITES = {"linkedin": 3000, "instagram": 2200, "x": 280}

WIKIPEDIA = "https://es.wikipedia.org/w/api.php"


@tool
def limites_de_plataforma(red: str) -> str:
    """Devuelve el limite de caracteres de una red social concreta.

    Usala cuando haya que ajustar una pieza al formato de una red. Acepta
    'linkedin', 'instagram' o 'x'.

    NO la uses para documentarte sobre un tema: para eso esta
    `buscar_en_wikipedia`.
    """
    clave = red.lower().strip()
    if clave not in LIMITES:
        return f"No tengo esa red. Conozco: {', '.join(LIMITES)}."
    return f"{clave}: {LIMITES[clave]} caracteres por publicacion."


@tool
def buscar_en_wikipedia(tema: str) -> str:
    """Busca un tema en Wikipedia y devuelve el arranque del articulo.

    Usala para documentarte sobre un tema ANTES de escribir una pieza sobre
    el: da contexto real, no inventado.

    NO la uses para limites ni normas de redes sociales: para eso esta
    `limites_de_plataforma`.
    """
    # Una sola llamada HTTP: busca el articulo mas cercano al tema y trae el
    # primer parrafo en texto plano. Sin API key: es la API publica.
    parametros = urllib.parse.urlencode(
        {
            "action": "query",
            "generator": "search",
            "gsrsearch": tema,
            "gsrlimit": 1,
            "prop": "extracts",
            "exintro": 1,
            "explaintext": 1,
            "format": "json",
        }
    )
    peticion = urllib.request.Request(
        f"{WIKIPEDIA}?{parametros}",
        # Wikipedia pide identificarse; sin User-Agent devuelve 403.
        headers={"User-Agent": "agente-contenido (curso Academia DigitalSoul)"},
    )
    with urllib.request.urlopen(peticion, timeout=10) as respuesta:
        dato = json.loads(respuesta.read())
    paginas = dato.get("query", {}).get("pages", {})
    if not paginas:
        return f"Wikipedia no encontro nada sobre '{tema}'."
    pagina = next(iter(paginas.values()))
    return f"{pagina['title']}: {pagina.get('extract', '').strip()[:600]}"


DEMO = [limites_de_plataforma, buscar_en_wikipedia]
