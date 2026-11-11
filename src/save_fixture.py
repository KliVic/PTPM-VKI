import sys
from pathlib import Path

import requests


DEFAULT_URL = "https://quotes.toscrape.com/"
DEFAULT_OUT = Path("tests/fixtures/quotes_page.html")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUT
    out.parent.mkdir(parents=True, exist_ok=True)

    print(f"Скачиваем: {url}")
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    response.encoding = response.apparent_encoding  # корректная кодировка

    out.write_text(response.text, encoding="utf-8")
    print(f"Сохранено как фикстура: {out} ({len(response.text)} символов)")


if __name__ == "__main__":
    main()