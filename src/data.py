"""Capa de datos: convierte la respuesta de Frankfurter en un DataFrame y cachea.

Responsabilidad: parseo + caché en memoria (st.cache_data, TTL 6 h).
No renderiza gráficas ni widgets.
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from . import frankfurter_client

CACHE_TTL_SECONDS = 6 * 60 * 60  # 21600 s = 6 horas


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_exchange_rates(base: str, symbols: list[str], start: date, end: date) -> pd.DataFrame:
    """Devuelve los tipos de cambio de `symbols` frente a `base` en [start, end].

    Entrada:
        base: código ISO de 3 letras.
        symbols: lista de códigos ISO, al menos 1.
        start/end: fechas con start <= end.

    Salida:
        DataFrame indexado por `date` (datetime) con una columna float por
        cada divisa de `symbols`.

    Errores:
        ValueError: `symbols` vacío o `start > end`.
        Propaga los errores de `frankfurter_client.fetch_rates`.
    """
    if not symbols:
        raise ValueError("Debe seleccionarse al menos una divisa de comparación.")
    if start > end:
        raise ValueError("La fecha de inicio no puede ser posterior a la fecha fin.")

    payload = frankfurter_client.fetch_rates(base, symbols, start, end)
    return payload_to_dataframe(payload, symbols)


def payload_to_dataframe(payload: dict, symbols: list[str]) -> pd.DataFrame:
    """Convierte el JSON crudo de Frankfurter en un DataFrame indexado por fecha.

    DataFrame vacío si la respuesta no contiene tasas para el rango pedido.
    """
    rates = payload.get("rates") or {}
    if not rates:
        return pd.DataFrame(columns=list(symbols), dtype=float)

    df = pd.DataFrame.from_dict(rates, orient="index")
    df.index = pd.to_datetime(df.index)
    df.index.name = "date"
    df = df.sort_index()

    # Asegura el contrato: una columna float por cada divisa solicitada,
    # incluso si alguna no aparece en alguna fecha (NA en días sin cotización).
    for symbol in symbols:
        if symbol not in df.columns:
            df[symbol] = float("nan")
    df = df[symbols].astype(float)
    return df
