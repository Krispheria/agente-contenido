# CLAUDE.md — agente-contenido

> Este archivo **es contenido del curso**, no un extra de producción. El informe 01 encontró que el
> riesgo número uno no es instalar nada: es que casi todo el material de LangChain que hay en
> internet —y buena parte de lo que un asistente escribe por defecto— es de la era 0.x y ya no
> funciona. Un `CLAUDE.md` con las versiones fijadas es la mitigación, y es el hábito que le sirve
> al alumno con cualquier librería.

## Versiones fijadas

Leídas de PyPI el 2026-08-10. **No las cambies sin decírmelo.**

| Paquete | Versión |
|---|---|
| `langchain` | 1.3.14 |
| `langgraph` | 1.2.10 |
| `langchain-openai` | 1.4.3 |
| `rich` | 15.0.0 |
| Python | 3.12 |

## Cómo se escribe código aquí

- **API 1.x, nunca 0.x.** Si vas a escribir `initialize_agent`, `AgentExecutor` o
  `langchain.retrievers`, para: eso es de 2024. La forma actual es `create_agent`, y lo legado vive
  en `langchain-classic`.
- **Consulta la documentación vigente antes de escribir**, no la memoria. Estas librerías llegaron
  a 1.0 el 2025-10-22 y ese salto rompió la forma de escribir agentes.
- **Un archivo, una idea.** Si una función no cabe en una pantalla, son dos pasos y se parte en dos
  nodos. Este código se lee en cámara.
- **Español en nombres del dominio** (`encargo`, `redactar`, `temas`), inglés solo en lo que impone
  la librería (`StateGraph`, `add_node`).
- Sin `try/except` decorativos ni capas de abstracción "por si acaso". Lo que no se explica en una
  frase, sobra.

## Lo que no se toca

- **El `.env` no se abre en pantalla nunca.** Al repositorio va `.env.example`, sin valores.
- `draw_mermaid_png()` **sale a internet**. En este proyecto se usa `draw_mermaid()`, que es texto
  local. No lo cambies.
- El trazado a LangSmith va apagado. Si algo lo enciende, se dice en voz alta.
