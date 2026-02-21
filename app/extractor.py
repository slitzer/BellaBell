import re
from decimal import Decimal, InvalidOperation

import httpx
from bs4 import BeautifulSoup


class ExtractionError(Exception):
    pass


def normalize_price(raw_text: str) -> float:
    cleaned = raw_text.strip().replace(",", "")
    match = re.search(r"[-+]?\d*\.?\d+", cleaned)
    if not match:
        raise ExtractionError("Could not parse a numeric price from extracted text.")

    try:
        return float(Decimal(match.group(0)).quantize(Decimal("0.01")))
    except InvalidOperation as exc:
        raise ExtractionError("Parsed value is not a valid decimal price.") from exc


def extract_price_by_css(url: str, css_selector: str, timeout_seconds: int = 10) -> tuple[str, float]:
    with httpx.Client(timeout=timeout_seconds, follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    node = soup.select_one(css_selector)
    if node is None:
        raise ExtractionError("CSS selector did not match any element.")

    raw_text = node.get_text(strip=True)
    parsed = normalize_price(raw_text)
    return raw_text, parsed
