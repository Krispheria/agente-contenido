"""Tools Use II — El mismo agente de `06_dos_tools.py`, dentro del panel.

Se ejecuta desde la raiz del proyecto:

    uv run Tools-Use-II/07_panel_tools.py
    uv run Tools-Use-II/07_panel_tools.py "Dame contexto sobre los agentes de IA"

El panel es el de la parte 2 y no se toca: pinta el grafo que le sirvan y
enciende los nodos segun llegan los pasos. El grafo real de `create_agent`
tiene un solo nodo `tools`, y eso no cuenta lo que importa: **que herramienta
eligio**. Por eso aqui el diagrama se genera de la lista de tools —una caja
por herramienta— y al ejecutar se enciende la que el modelo pidio de verdad.

La pregunta se fija al arrancar el servidor: para probar la otra herramienta,
se para (Ctrl+C) y se arranca con otra pregunta.
"""

import json
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# Este script vive en su carpeta de clase; el paquete `agente` y la carpeta
# `panel/` estan un nivel arriba.
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from langchain.agents import create_agent
from langchain_core.callbacks import get_usage_metadata_callback
from langchain_openai import ChatOpenAI

from herramientas_demo import DEMO
from agente.nodos import MODELO_MECANICO
from agente.precios import FECHA_PRECIOS, coste

# Puerto propio: puede convivir con el panel de la cadena (4571).
PUERTO = 4572
PANEL = RAIZ / "panel"

PREGUNTA_DEFECTO = "Voy a publicar en Instagram. Cuantos caracteres tengo?"
PREGUNTA = " ".join(sys.argv[1:]).strip() or PREGUNTA_DEFECTO

INSTRUCCIONES = (
    "Eres el asistente de contenido de DigitalSoul. Antes de proponer nada, "
    "usa las herramientas que tienes. No inventes datos que puedas consultar."
)

TIPOS = {
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
}


def construir_agente():
    modelo = ChatOpenAI(model=MODELO_MECANICO, temperature=0, reasoning_effort="none")
    return create_agent(model=modelo, tools=DEMO, system_prompt=INSTRUCCIONES)


def mermaid_del_agente() -> str:
    """El diagrama sale de la lista de tools, no de LangGraph.

    `create_agent` dibuja un unico nodo `tools`, valga la herramienta que
    valga. Para ver la eleccion, cada tool es su propia caja, colgando del
    modelo y volviendo a el.
    """
    lineas = ["graph TD;", "\t__start__([__start__]) --> model(model);"]
    for herramienta in DEMO:
        nombre = herramienta.name
        lineas.append(f"\tmodel -.-> {nombre}({nombre});")
        lineas.append(f"\t{nombre} -.-> model;")
    lineas.append("\tmodel -.-> __end__([__end__]);")
    return "\n".join(lineas)


def _nodos_del_paso(paso) -> list[dict]:
    """Traduce cada paso del agente a los nodos del diagrama.

    El paso `tools` se convierte en la herramienta que corrio (su nombre viene
    en el ToolMessage); el paso `model` se anota con lo que pidio o respondio.
    """
    nodos = []
    for nodo, cambios in paso.items():
        mensajes = (cambios or {}).get("messages", []) or []
        if nodo == "tools":
            for mensaje in mensajes:
                nodos.append(
                    {
                        "nombre": mensaje.name,
                        "cambios": {"devuelve": _recortar(mensaje.content)},
                    }
                )
            continue
        anotado = {}
        for mensaje in mensajes:
            for peticion in getattr(mensaje, "tool_calls", None) or []:
                anotado["pide"] = f"{peticion['name']} {peticion['args']}"
            if getattr(mensaje, "content", ""):
                anotado["respuesta"] = _recortar(mensaje.content)
        nodos.append({"nombre": nodo, "cambios": anotado or {"paso": _recortar(cambios)}})
    return nodos


class Servidor(BaseHTTPRequestHandler):
    def do_GET(self):
        self.path = self.path.split("?", 1)[0]
        if self.path in ("/", "/index.html"):
            self._archivo("index.html")
        elif self.path == "/panel.js":
            self._archivo("panel.js")
        elif self.path == "/mermaid.js":
            self._archivo("mermaid.js")
        elif self.path == "/grafo":
            self._json({"mermaid": mermaid_del_agente()})
        elif self.path == "/ejecutar":
            self._ejecutar()
        else:
            self.send_error(404)

    def _archivo(self, nombre: str):
        ruta = PANEL / nombre
        if not ruta.exists():
            self.send_error(404, f"falta {nombre}")
            return
        cuerpo = ruta.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", TIPOS.get(ruta.suffix, "text/plain"))
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def _json(self, dato):
        cuerpo = json.dumps(dato, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def _ejecutar(self):
        """El mismo Server-Sent Events de `03_panel.py`, con el agente dentro."""
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()

        agente = construir_agente()
        entrada = {"messages": [{"role": "user", "content": PREGUNTA}]}
        try:
            with get_usage_metadata_callback() as uso:
                for paso in agente.stream(entrada, stream_mode="updates"):
                    acumulado = dict(uso.usage_metadata)
                    self._evento(
                        {
                            "nodos": _nodos_del_paso(paso),
                            "uso": acumulado,
                            "coste": coste(acumulado),
                            "fecha_precios": FECHA_PRECIOS,
                        }
                    )
            self._evento(
                {
                    "fin": True,
                    "uso": uso.usage_metadata,
                    "coste": coste(uso.usage_metadata),
                    "fecha_precios": FECHA_PRECIOS,
                }
            )
        except Exception as error:  # el fallo tambien se ve en el panel
            self._evento({"error": f"{type(error).__name__}: {error}"})

    def _evento(self, dato):
        linea = f"data: {json.dumps(dato, ensure_ascii=False)}\n\n"
        self.wfile.write(linea.encode("utf-8"))
        self.wfile.flush()

    def log_message(self, *_):
        """Silencio. La terminal se graba y no queremos ruido de peticiones."""


def _recortar(valor, tope=400):
    texto = str(valor)
    return texto if len(texto) <= tope else texto[:tope] + "..."


if __name__ == "__main__":
    servidor = ThreadingHTTPServer(("127.0.0.1", PUERTO), Servidor)
    url = f"http://localhost:{PUERTO}"
    print(f"Panel en {url}   (Ctrl+C para parar)")
    print(f"Pregunta fijada: {PREGUNTA}")
    threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nPanel parado.")
