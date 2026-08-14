# agente-contenido

El proyecto sobre el que se graba **Agentes 1 · Flujos agénticos avanzados**. Crece parte a parte:
aquí está la línea recta, y en las partes 3 a 6 se le añaden tools, una bifurcación, llamadas en
paralelo y una parada para pedir permiso.

**Repositorio propio**, fuera del control de versiones del vault:
[`Krispheria/agente-contenido`](https://github.com/Krispheria/agente-contenido) (creado el
2026-08-14, **privado** hasta que salga el curso). Es lo que se le entrega al alumno: se clona, se
hace `uv sync` y ya está corriendo lo mismo que sale en el vídeo. El `.env` nunca entra aquí — al
repositorio va `.env.example`, sin valores.

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
| `agente/herramientas.py` | Las tools, en cuatro variantes de nombre y descripción (parte 3) |
| `encargo.md` | El encargo del mes: el texto suelto que entra al agente |
| `historico-publicaciones.json` | Lo ya publicado, para que la tool no repita ángulos |
| `CLAUDE.md` | Las versiones fijadas y cómo se escribe código aquí |

## Las demos

Un script por concepto. Se abre, se ejecuta delante de la clase, y **va escribiendo lo que hace
mientras lo hace**. Esa es la premisa del curso: no explicar el routing, verlo enrutar.

El número del archivo es el orden en que se construyeron, no el de las diapositivas.

| Script | Parte · diapositiva | Qué se ve al ejecutarlo |
|---|---|---|
| `00_ejecutar.py` | 1 · dia. 7 y 2 · dia. 10 | La caja negra: solo la pieza. Y sin `.env`, el error de credenciales |
| `01_dibujar.py` | 2 · dia. 12 | El mapa del flujo: los pasos y su orden |
| `02_traza.py` | 2 · dia. 13 | Cada nodo, según termina, con lo que cambió y lo que costó |
| `03_panel.py` | 2 · dia. 11 y 14 | El diagrama encendiéndose, con el gasto subiendo al lado |
| `04_llamada_cruda.py` | 3 · dia. 19–21 | La API pelada: el modelo **pide** una función y no la ejecuta |
| `05_tools.py` | 3 · dia. 22–26 | El agente con herramientas, y el docstring decidiendo la elección |
| `06_routing.py` | 4 | La rama elegida, y por qué |
| `07_paralelo.py` | 5 | Tres llamadas saliendo a la vez, con cronómetro |
| `08_humano.py` | 6 | El agente parándose a esperarte, y el aviso en Telegram |

Escritos: del `00` al `05`. El resto llega parte a parte.

`05_tools.py` admite banderas para las demos de la parte 3: `--vagas`, `--opacas`, `--rescatadas`
(las mismas herramientas con distinto nombre y docstring), `--limite` (la pregunta que solo una puede
responder) y `--revienta` (una red que la tool no conoce).

## Lo primero que hay que ver

```powershell
uv run 01_dibujar.py
uv run 02_traza.py
uv run 03_panel.py
```

El primero saca el diagrama en texto Mermaid y no necesita clave; el segundo ejecuta el agente y
escribe los pasos según ocurren; el tercero levanta el panel en `http://localhost:4571`. Si los tres
funcionan, el proyecto está montado y el resto del curso se apoya aquí.
