import requests
from bs4 import BeautifulSoup


class ForumParser:
    """Парсер форумной страницы. Селекторы подобраны под фикстуру."""

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    def __init__(self, headers=None, timeout: int = 10):
        self.headers = headers or self.DEFAULT_HEADERS
        self.timeout = timeout

    def parse_page(self, url: str):
        """Скачивает страницу и возвращает разобранные комментарии."""
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return self.parse_html(response.text)

    def parse_html(self, html: str):
        """Разбирает HTML-строку. Используется в тестах вместо сети."""
        soup = BeautifulSoup(html, "lxml")
        results = []

        for node in soup.select("div.comment[data-id]"):
            comment_id_raw = (node.get("data-id") or "").strip()
            username_node = node.select_one(".username")
            message_node = node.select_one(".message")

            if not comment_id_raw or username_node is None or message_node is None:
                continue

            try:
                comment_id = int(comment_id_raw)
            except ValueError:
                continue

            results.append(
                {
                    "id": comment_id,
                    "name": username_node.get_text(strip=True),
                    "message": message_node.decode_contents().strip(),
                }
            )

        return results

    def save_to_db(self, parsed_data, repository) -> int:
        """Сохраняет данные в БД. Возвращает количество добавленных записей."""
        saved = 0
        for item in parsed_data:
            try:
                repository.add(item["id"], item["name"], item["message"])
                saved += 1
            except ValueError:
                # дубликат id, слишком длинное сообщение и т.п. — пропускаем
                continue
        return saved