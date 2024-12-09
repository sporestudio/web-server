import pytest
from app import shortener_url

def test_generate_short_url():
    original_url = "https://example.com"
    short_url = shortener_url(original_url)
    assert len(short_url) == 6
    assert short_url.isalnum()