import pytest

from app.extractor import normalize_price, ExtractionError


def test_normalize_price_parses_currency_text():
    assert normalize_price("NZ$1,299.95") == 1299.95


def test_normalize_price_raises_on_invalid_value():
    with pytest.raises(ExtractionError):
        normalize_price("price unavailable")
