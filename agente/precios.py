"""Cuanto cuesta lo que acabas de ejecutar.

**Ninguna libreria sabe el precio de hoy.** Los tokens te los da la API; el
precio lo pones tu, a mano, desde la tabla de OpenAI. Esta constante caduca, y
decirlo en voz alta es parte de la leccion.

Precios por millon de tokens, leidos el **2026-08-10**.
Fuente: investigacion/04-paralelo-limites-coste.md
"""

# modelo -> (entrada, salida) en dolares por millon de tokens
PRECIOS = {
    "gpt-5.6-luna": (0.20, 1.20),
    "gpt-5.6-terra": (2.00, 12.00),
    "gpt-5.6-sol": (5.00, 30.00),
}

FECHA_PRECIOS = "2026-08-10"


def coste(uso: dict) -> float:
    """Convierte el uso de una ejecucion en dolares.

    `uso` es lo que devuelve `get_usage_metadata_callback()`: un diccionario
    `{nombre_del_modelo: {"input_tokens": N, "output_tokens": N, ...}}`.
    """
    total = 0.0
    for modelo, tokens in uso.items():
        if modelo not in PRECIOS:
            continue  # modelo sin precio en la tabla: no se inventa
        precio_entrada, precio_salida = PRECIOS[modelo]
        total += tokens.get("input_tokens", 0) / 1_000_000 * precio_entrada
        total += tokens.get("output_tokens", 0) / 1_000_000 * precio_salida
    return total
