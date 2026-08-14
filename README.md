# agente-contenido

El proyecto sobre el que se graba **Agentes 1 · Flujos agénticos avanzados**. Crece parte a parte:
aquí está la línea recta, y en las partes 3 a 6 se le añaden tools, una bifurcación, llamadas en
paralelo y una parada para pedir permiso.

Repositorio propio, fuera del control de versiones del vault.

## Arrancar

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```powershell
uv sync
```

`uv` se descarga el Python 3.12 solo si no lo tienes, crea el `.venv` y resuelve las versiones
fijadas. **No hay que activar nada**: `uv run` entra en el entorno por su cuenta, que es justo el
paso donde Windows tumba a los principiantes.

Después, copia `.env.example` a `.env` y pon tu clave de OpenAI.

## Los archivos

| Archivo | Qué es |
|---|---|
| `agente/estado.py` | Qué datos viajan por el grafo |
| `agente/nodos.py` | Qué hace cada paso |
| `agente/grafo.py` | Cómo se conectan |
| `encargo.md` | El encargo del mes: el texto suelto que entra al agente |
| `CLAUDE.md` | Las versiones fijadas y cómo se escribe código aquí |

## Las demos

Un script por concepto. Se abre, se ejecuta delante de la clase, y **va escribiendo lo que hace
mientras lo hace**. Esa es la premisa del curso: no explicar el routing, verlo enrutar.

El número del archivo es el orden en que se construyeron, no el de las diapositivas.

| Script | Parte · diapositiva | Qué se ve al ejecutarlo |
|---|---|---|
| `00_ejecutar.py` | 1 · dia. 7 y 2 · dia. 10 | La caja negra: solo la pieza. Y sin `.env`, el error de credenciales |
| `01_dibujar.py` | 2 · dia. 12 | El mapa del flujo: los pasos y su orden |
| `02_traza.py` | 2 · dia. 13 | Cada nodo, según termina, con lo que cambió |
| `03_panel.py` | 2 · dia. 11 y 14 | El diagrama encendiéndose, con el coste al lado |
| `04_tools.py` | 3 | El modelo pidiendo la tool y tu código ejecutándola |
| `05_routing.py` | 4 | La rama elegida, y por qué |
| `06_paralelo.py` | 5 | Tres llamadas saliendo a la vez, con cronómetro |
| `07_humano.py` | 6 | El agente parándose a esperarte, y el aviso en Telegram |

Escritos: `00`, `01`, `02` y `03`. El resto llega parte a parte.

## Lo primero que hay que ver

```powershell
uv run 01_dibujar.py
uv run 02_traza.py
uv run 03_panel.py
```

El primero saca el diagrama en texto Mermaid y no necesita clave; el segundo ejecuta el agente y
escribe los pasos según ocurren; el tercero levanta el panel en `http://localhost:4571`. Si los tres
funcionan, el proyecto está montado y el resto del curso se apoya aquí.
