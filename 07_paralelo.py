"""Diapositivas 35 a 43 — Mismas llamadas, distinto calendario.

    uv run 07_paralelo.py --modo secuencial
    uv run 07_paralelo.py --modo paralelo
    uv run 07_paralelo.py --modo abanico
    uv run 07_paralelo.py --modo sin-tope --cantidad 30
    uv run 07_paralelo.py --modo protegido --cantidad 30 --concurrencia 3

Paralelizar reduce la espera, no la factura: los tokens y el coste se imprimen
en todos los modos para poder comprobarlo con una ejecución real.
"""

import argparse
import asyncio
import os
import random
import time

from dotenv import load_dotenv
from langchain_core.callbacks import get_usage_metadata_callback
from openai import RateLimitError
from rich.console import Console

from agente.grafo import construir
from agente.nodos import MAX_TOKENS_REDACCION, MODELO_REDACCION, _modelo
from agente.precios import FECHA_PRECIOS, coste

consola = Console()
PROMPTS = [
    "Escribe una versión para LinkedIn sobre la diferencia entre un chat y un agente.",
    "Escribe una versión para Instagram sobre la diferencia entre un chat y un agente.",
    "Escribe una versión para X sobre la diferencia entre un chat y un agente.",
]


def comprobar_clave() -> None:
    """Falla antes de crear el cliente si todavía no se configuró el proyecto."""
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        consola.print(
            "[red]Falta OPENAI_API_KEY.[/] Copia .env.example a .env y añade tu clave."
        )
        raise SystemExit(1)


def resumen_uso(uso: dict) -> tuple[int, int]:
    """Suma lo que devuelve la API aunque intervenga más de un modelo."""
    entrada = sum(datos.get("input_tokens", 0) for datos in uso.values())
    salida = sum(datos.get("output_tokens", 0) for datos in uso.values())
    return entrada, salida


def imprimir_factura(modo: str, segundos: float, uso: dict) -> None:
    """Imprime los cinco datos que se anotan al medir cada modalidad."""
    entrada, salida = resumen_uso(uso)
    consola.rule(modo)
    consola.print(f"Tiempo total: {segundos:.2f} s")
    consola.print(f"Tokens de entrada: {entrada}")
    consola.print(f"Tokens de salida: {salida}")
    consola.print(f"Coste: ${coste(uso):.6f}")
    consola.print(f"Precios del: {FECHA_PRECIOS}")


async def ejecutar_llamadas(modo: str, cantidad: int, concurrencia: int) -> None:
    """Ejecuta la misma tarea en fila, junta o protegida con un semáforo."""
    modelo = _modelo(MODELO_REDACCION, max_tokens=MAX_TOKENS_REDACCION)
    prompts = (PROMPTS[:2] if modo in {"secuencial", "paralelo"} else PROMPTS) * cantidad

    with get_usage_metadata_callback() as uso:
        inicio = time.perf_counter()
        if modo == "secuencial":
            for prompt in prompts:
                await modelo.ainvoke(prompt)
        elif modo in {"paralelo", "sin-tope"}:
            await asyncio.gather(*(modelo.ainvoke(prompt) for prompt in prompts))
        else:
            semaforo = asyncio.Semaphore(concurrencia)
            await asyncio.gather(
                *(llamar_con_reintentos(modelo, prompt, semaforo) for prompt in prompts)
            )
        segundos = time.perf_counter() - inicio

    imprimir_factura(modo, segundos, uso.usage_metadata)


async def llamar_con_reintentos(modelo, prompt: str, semaforo: asyncio.Semaphore):
    """Espera más tras un 429 para no repetir la misma ráfaga."""
    for intento in range(4):
        try:
            async with semaforo:
                return await modelo.ainvoke(prompt)
        except RateLimitError as error:
            if intento == 3:
                imprimir_limite(error)
                raise
            espera = min(2**intento + random.uniform(0, 1), 60)
            consola.print(f"429: reintento {intento + 1} en {espera:.1f} s")
            await asyncio.sleep(espera)


def imprimir_limite(error: RateLimitError) -> None:
    """Muestra los datos reales del límite cuando la API devuelve un 429."""
    consola.rule("La API ha respondido 429")
    respuesta = getattr(error, "response", None)
    cabeceras = getattr(respuesta, "headers", {})
    for nombre in ("Retry-After",):
        if valor := cabeceras.get(nombre):
            consola.print(f"{nombre}: {valor}")
    for prefijo in ("x-ratelimit-limit-", "x-ratelimit-remaining-", "x-ratelimit-reset-"):
        for nombre, valor in cabeceras.items():
            if nombre.lower().startswith(prefijo):
                consola.print(f"{nombre}: {valor}")


async def ejecutar_abanico() -> None:
    """Deja que el grafo abra sus tres ramas y reúna los borradores."""
    with get_usage_metadata_callback() as uso:
        inicio = time.perf_counter()
        resultado = await asyncio.to_thread(construir().invoke, {})
        segundos = time.perf_counter() - inicio

    consola.print(f"Borradores reunidos: {len(resultado.get('borradores', []))}")
    imprimir_factura("abanico", segundos, uso.usage_metadata)


def argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compara llamadas secuenciales y paralelas.")
    parser.add_argument(
        "--modo",
        choices=["secuencial", "paralelo", "abanico", "sin-tope", "protegido"],
        required=True,
    )
    parser.add_argument("--cantidad", type=int, default=1)
    parser.add_argument("--concurrencia", type=int, default=3)
    opciones = parser.parse_args()
    if opciones.cantidad < 1 or opciones.concurrencia < 1:
        parser.error("--cantidad y --concurrencia deben ser mayores que cero.")
    return opciones


async def principal() -> None:
    opciones = argumentos()
    comprobar_clave()
    try:
        if opciones.modo == "abanico":
            await ejecutar_abanico()
        else:
            await ejecutar_llamadas(
                opciones.modo, opciones.cantidad, opciones.concurrencia
            )
    except RateLimitError as error:
        imprimir_limite(error)
    except Exception as error:
        consola.print(f"[red]La ejecución ha fallado:[/] {type(error).__name__}: {error}")


if __name__ == "__main__":
    asyncio.run(principal())
