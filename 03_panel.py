"""Diapositivas 11 y 14 — El panel: el grafo se enciende por donde va pasando.

    uv run 03_panel.py

Levanta un servidor en http://localhost:4571 y abre el navegador. Le das a
Ejecutar y ves el diagrama encenderse nodo a nodo, con los tokens y el coste
subiendo al lado.

Por dentro no hay nada nuevo: es **el mismo bucle de `02_traza.py`**. Alli cada
paso se escribia en la terminal; aqui se manda al navegador. El mecanismo es el
de siempre, `stream(stream_mode="updates")`.

Sin cuentas, sin servicios externos y sin red: todo ocurre en tu maquina.
"""

import json
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from langchain_core.callbacks import get_usage_metadata_callback

from agente.grafo import construir
from agente.precios import FECHA_PRECIOS, coste

PUERTO = 4571
PANEL = Path(__file__).resolve().parent / "panel"

TIPOS = {
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
}


class Servidor(BaseHTTPRequestHandler):
    def do_GET(self):
        # Sin esto, un `?v=2` para saltarse la cache devuelve 404.
        self.path = self.path.split("?", 1)[0]
        if self.path in ("/", "/index.html"):
            self._archivo("index.html")
        elif self.path == "/panel.js":
            self._archivo("panel.js")
        elif self.path == "/mermaid.js":
            self._archivo("mermaid.js")
        elif self.path == "/grafo":
            self._json({"mermaid": construir().get_graph().draw_mermaid()})
        elif self.path == "/ejecutar":
            self._ejecutar()
        else:
            self.send_error(404)

    # --- las tres respuestas -------------------------------------------------

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
        """Ejecuta el agente y va mandando cada paso al navegador segun ocurre.

        Server-Sent Events: una conexion abierta por la que el servidor escribe
        lineas `data: {...}` cuando tiene algo que contar. El navegador las
        recibe con `EventSource`. Es lo mas simple que hay para "empujar" datos.
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()

        grafo = construir()
        try:
            # El contador va sumando los tokens de todas las llamadas que ocurran
            # dentro del `with`. La gracia es que se puede **mirar por el camino**:
            # al terminar cada paso ya lleva contadas las llamadas de ese paso, y
            # de ahi sale el gasto subiendo en pantalla.
            with get_usage_metadata_callback() as uso:
                # Cada `paso` es un super-step: la tanda de nodos que LangGraph
                # acaba de ejecutar. Normalmente es uno, pero cuando el grafo se
                # abre en abanico son varios **a la vez** (parte 5) — y el panel
                # los enciende juntos, que es lo que un log no puede mostrar.
                for paso in grafo.stream({}, stream_mode="updates"):
                    acumulado = dict(uso.usage_metadata)
                    self._evento(
                        {
                            "nodos": [
                                {
                                    "nombre": nodo,
                                    "cambios": {
                                        campo: _recortar(valor)
                                        for campo, valor in cambios.items()
                                    },
                                }
                                for nodo, cambios in paso.items()
                            ],
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
    threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nPanel parado.")
