"""Cliente HTTP para la API pública de Frankfurter (sin autenticación).

Responsabilidad: encapsular las llamadas HTTP y devolver el JSON crudo.
No parsea a DataFrame, no cachea, no toca la interfaz.
"""

from __future__ import annotations

from datetime import date

import requests

API_BASE_URL = "https://api.frankfurter.dev/v1"
DEFAULT_TIMEOUT = 10  # segundos


def build_url(start: date, end: date) -> str:
    """Construye la URL del endpoint de histórico con el rango `start..end`."""
    return f"{API_BASE_URL}/{start.isoformat()}..{end.isoformat()}"


def fetch_rates(base: str, symbols: list[str], start: date, end: date) -> dict:
    """Obtiene los tipos de cambio de `symbols` frente a `base` en [start, end].

    Entrada:
        base: código ISO de 3 letras (obligatorio).
        symbols: lista de códigos ISO (obligatorio, mínimo 1).
        start/end: fechas con start <= end.

    Salida:
        JSON crudo de Frankfurter, p. ej.
        {"amount": 1.0, "base": "EUR", "rates": {"2026-06-01": {"USD": 1.085}}}

    Errores:
        requests.ConnectionError: fallo de red.
        requests.RequestException: error HTTP (divisa inválida 404, rango
        inválido, etc.). El código de estado queda en `.response.status_code`
        y en el mensaje de la excepción.
    """
    params = {"base": base, "symbols": ",".join(symbols)}
    response = requests.get(build_url(start, end), params=params, timeout=DEFAULT_TIMEOUT)

    if response.status_code >= 400:
        raise requests.RequestException(
            f"Frankfurter API devolvió el código {response.status_code}",
            response=response,
        )

    return response.json()
