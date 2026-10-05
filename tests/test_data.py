"""Tests unitarios de data — la red está mockeada (nunca se llama a Frankfurter)."""

from __future__ import annotations

from datetime import date
from unittest.mock import patch

import pandas as pd
import pytest

from src.data import get_exchange_rates, payload_to_dataframe

API_PAYLOAD = {
    "amount": 1.0,
    "base": "EUR",
    "dates": ["2026-06-01", "2026-06-02", "2026-06-03"],
    "rates": {
        "2026-06-01": {"USD": 1.085, "GBP": 0.855},
        "2026-06-02": {"USD": 1.087, "GBP": 0.853},
        "2026-06-03": {"USD": 1.084, "GBP": 0.856},
    },
}


def test_get_exchange_rates_shapes_dataframe():
    # TEST-001: respuesta válida con 2 divisas y 3 fechas
    with patch("src.data.frankfurter_client.fetch_rates", return_value=API_PAYLOAD) as mock_fetch:
        df = get_exchange_rates("EUR", ["USD", "GBP"], date(2026, 6, 1), date(2026, 6, 3))

    assert isinstance(df, pd.DataFrame)
    assert df.shape == (3, 2)
    assert list(df.columns) == ["USD", "GBP"]
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.index.name == "date"
    assert df.loc["2026-06-01", "USD"] == 1.085
    mock_fetch.assert_called_once()


def test_get_exchange_rates_empty_symbols_raises_value_error():
    # TEST-003: symbols vacío -> ValueError
    with pytest.raises(ValueError):
        get_exchange_rates("EUR", [], date(2026, 6, 1), date(2026, 6, 3))


def test_get_exchange_rates_start_after_end_raises_value_error():
    # TEST-004: start > end -> ValueError
    with pytest.raises(ValueError):
        get_exchange_rates("EUR", ["USD"], date(2026, 6, 3), date(2026, 6, 1))


def test_get_exchange_rates_empty_api_response_returns_empty_dataframe():
    with patch("src.data.frankfurter_client.fetch_rates", return_value={"rates": {}}):
        df = get_exchange_rates("EUR", ["USD"], date(2025, 1, 1), date(2025, 1, 31))

    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_get_exchange_rates_propagates_api_error():
    import requests

    with patch(
        "src.data.frankfurter_client.fetch_rates",
        side_effect=requests.RequestException("404"),
    ):
        with pytest.raises(requests.RequestException):
            get_exchange_rates("EUR", ["XXX"], date(2024, 1, 1), date(2024, 1, 31))


def test_payload_to_dataframe_orders_and_sorts_by_date():
    payload = {
        "rates": {
            "2026-06-03": {"USD": 1.084},
            "2026-06-01": {"USD": 1.085},
            "2026-06-02": {"USD": 1.087},
        }
    }
    df = payload_to_dataframe(payload, ["USD"])

    assert list(df.index.astype(str)) == ["2026-06-01", "2026-06-02", "2026-06-03"]
    assert df["USD"].dtype == float


def test_payload_to_dataframe_adds_missing_symbol_as_na():
    payload = {"rates": {"2026-06-01": {"USD": 1.085}}}
    df = payload_to_dataframe(payload, ["USD", "GBP"])

    assert list(df.columns) == ["USD", "GBP"]
    assert pd.isna(df.loc["2026-06-01", "GBP"])
