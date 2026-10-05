"""Dashboard de tipos de cambio — punto de entrada de Streamlit.

Interfaz: selectors, gráfica de líneas y tabla.
No hace llamadas HTTP directas ni transformaciones de datos complejas.
"""

from __future__ import annotations

from datetime import date, timedelta

import requests
import streamlit as st

from src.data import get_exchange_rates

st.set_page_config(page_title="Evolución de tipos de cambio", layout="wide")

# Divisas soportadas por la API de Frankfurter.
CURRENCIES = [
    "AUD", "BGN", "BRL", "CAD", "CHF", "CNY", "CZK", "DKK", "EUR", "GBP",
    "HKD", "HUF", "IDR", "ILS", "INR", "ISK", "JPY", "KRW", "MXN", "MYR",
    "NOK", "NZD", "PHP", "PLN", "RON", "SEK", "SGD", "THB", "TRY", "USD",
    "ZAR",
]

TODAY = date.today()
DEFAULT_START = TODAY - timedelta(days=90)

st.title("Evolución histórica de tipos de cambio")

col_base, col_quotes, col_dates = st.columns([1, 2, 2])

with col_base:
    base = st.selectbox("Divisa base", CURRENCIES, index=CURRENCIES.index("EUR"))
with col_quotes:
    quotes = st.multiselect(
        "Divisas a comparar frente a la base",
        [c for c in CURRENCIES if c != base],
        default=["USD", "GBP"],
    )
with col_dates:
    date_range = st.date_input(
        "Rango de fechas",
        value=(DEFAULT_START, TODAY),
        min_value=date(1999, 1, 1),
        max_value=TODAY,  # no se permiten fechas futuras
    )

# --- Validaciones de interfaz (sección 10) ---------------------------------
if len(date_range) != 2:
    st.info("Selecciona una fecha de inicio y una fecha fin.")
    st.stop()

start, end = date_range

if start > end:
    st.warning("La fecha de inicio no puede ser posterior a la fecha fin.")
    st.stop()

if not quotes:
    st.warning("Selecciona al menos una divisa de comparación para ver la gráfica.")
    st.stop()

# --- Datos -------------------------------------------------------------------
try:
    df = get_exchange_rates(base, quotes, start, end)
except ValueError as exc:
    st.warning(str(exc))
    st.stop()
except requests.ConnectionError:
    st.error("No se han podido obtener los datos. Inténtalo de nuevo más tarde.")
    st.stop()
except requests.RequestException as exc:
    status = getattr(getattr(exc, "response", None), "status_code", None)
    if status == 404:
        st.warning("La divisa seleccionada no está disponible.")
    else:
        st.error("No se han podido obtener los datos. Inténtalo de nuevo más tarde.")
    st.stop()
except Exception:  # noqa: BLE001 — nunca mostrar excepciones al usuario
    st.error("No se han podido obtener los datos. Inténtalo de nuevo más tarde.")
    st.stop()

if df is None or df.empty:
    st.info("No hay datos para el rango seleccionado.")
    st.stop()

# --- Render -------------------------------------------------------------------
st.subheader(f"{base} frente a {', '.join(quotes)}")
st.line_chart(df, width="stretch")

with st.expander("Tabla de datos"):
    st.dataframe(df, width="stretch")
