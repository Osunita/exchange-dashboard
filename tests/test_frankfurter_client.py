"""Tests unitarios de frankfurter_client — la red está mockeada."""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

import pytest
import requests

from src import frankfurter_client

START = date(2026, 6, 1)
END = date(2026, 6, 3)


def _response(status_code: int, payload: dict | None = None) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = payload or {}
    return response


@patch("src.frankfurter_client.requests.get")
def test_fetch_rates_returns_raw_json(mock_get):
    payload = {"amount": 1.0, "base": "EUR", "rates": {"2026-06-01": {"USD": 1.085}}}
    mock_get.return_value = _response(200, payload)

    result = frankfurter_client.fetch_rates("EUR", ["USD"], START, END)

    assert result == payload
    url = mock_get.call_args.args[0]
    assert "2026-06-01..2026-06-03" in url
    params = mock_get.call_args.kwargs["params"]
    assert params["base"] == "EUR"
    assert params["symbols"] == "USD"


@patch("src.frankfurter_client.requests.get")
def test_fetch_rates_multiple_symbols(mock_get):
    mock_get.return_value = _response(200, {"rates": {}})

    frankfurter_client.fetch_rates("EUR", ["USD", "GBP"], START, END)

    params = mock_get.call_args.kwargs["params"]
    assert params["symbols"] == "USD,GBP"


def test_fetch_rates_404_raises_with_status_code():
    # TEST-002: la API devuelve 404 (divisa no soportada) -> excepción con código
    response = _response(404)
    with patch("src.frankfurter_client.requests.get", return_value=response):
        with pytest.raises(requests.RequestException) as excinfo:
            frankfurter_client.fetch_rates("EUR", ["XXX"], START, END)

    assert excinfo.value.response.status_code == 404
    assert "404" in str(excinfo.value)


def test_fetch_rates_connection_error_propagates():
    with patch(
        "src.frankfurter_client.requests.get",
        side_effect=requests.ConnectionError("network down"),
    ):
        with pytest.raises(requests.ConnectionError):
            frankfurter_client.fetch_rates("EUR", ["USD"], START, END)
