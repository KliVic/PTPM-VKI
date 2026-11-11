import requests
from bs4 import BeautifulSoup


class ForumParser:
    """
    Парсер форумной страницы с настраиваемыми CSS-селекторами.

    Поддерживает два режима извлечения id:
      - id_attr="data-id" — берётся из HTML-атрибута (обязательно целое);
      - id_attr=None      — генерируется порядковый номер по порядку элементов.
    """

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    def __init__(
        self,
        item_selector: str,
        name_selector: str,
        message_selector: str,
        id_attr: str | None = "data-id",
        headers: dict | None = None,
        timeout: int = 10,
    ):
        self.item_selector = item_selector
        self.name_selector = name_selector
        self.message_selector = message_selector
        self.id_attr = id_attr
        self.headers = headers or self.DEFAULT_HEADERS
        self.timeout = timeout

    #готовые профили под конкретные сайты

    @classmethod
    def for_quotes_toscrape(cls, **kwargs) -> "ForumParser":
        """Профиль под https://quotes.toscrape.com (без числового id в разметке)."""
        return cls(
            item_selector="div.quote",
            name_selector="small.author",
            message_selector="span.text",
            id_attr=None,
            **kwargs,
        )

    @classmethod
    def for_fixture(cls, **kwargs) -> "ForumParser":
        return cls(
            item_selector="div.comment[data-id]",
            name_selector=".username",
            message_selector=".message",
            id_attr="data-id",
            **kwargs,
        )

    #основная логика

    def parse_page(self, url: str):
        """Скачивает страницу и возвращает разобранные записи."""
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return self.parse_html(response.text)

    def parse_html(self, html: str):
        """Разбирает HTML-строку. В тестах используется вместо сети."""
        soup = BeautifulSoup(html, "lxml")
        results = []

        for index, node in enumerate(soup.select(self.item_selector), start=1):
            name_node = node.select_one(self.name_selector)
            message_node = node.select_one(self.message_selector)

            if name_node is None or message_node is None:
                continue

            comment_id = self._extract_id(node, index)
            if comment_id is None:
                continue

            results.append(
                {
                    "id": comment_id,
                    "name": name_node.get_text(strip=True),
                    "message": message_node.decode_contents().strip(),
                }
            )

        return results

    def _extract_id(self, node, fallback: int):
        if self.id_attr is None:
            return fallback

        raw = (node.get(self.id_attr) or "").strip()
        if not raw:
            return None
        try:
            return int(raw)
        except ValueError:
            return None

    def save_to_db(self, parsed_data, repository) -> int:
        """Сохраняет данные в БД. Возвращает количество добавленных записей."""
        saved = 0
        for item in parsed_data:
            try:
                repository.add(item["id"], item["name"], item["message"])
                saved += 1
            except ValueError:
                continue
        return saved