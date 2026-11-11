import unittest
from pathlib import Path

from src.database import DatabaseRepository
from src.parser import ForumParser

FIXTURES = Path(__file__).parent / "fixtures"


class TestForumParserQuotesSite(unittest.TestCase):
    """Профиль под quotes.toscrape.com. Фикстура = реальная страница, 10 цитат."""

    def setUp(self):
        self.parser = ForumParser.for_quotes_toscrape()
        self.html = (FIXTURES / "quotes_page.html").read_text(encoding="utf-8")

    # 1: количество цитат совпадает
    def test_parse_html_returns_ten_quotes(self):
        result = self.parser.parse_html(self.html)
        self.assertEqual(len(result), 10)

    # 2: id присваиваются по порядку 1..10
    def test_parse_html_assigns_sequential_ids(self):
        result = self.parser.parse_html(self.html)
        self.assertEqual([item["id"] for item in result], list(range(1, 11)))

    # 3: первая цитата извлечена корректно
    def test_parse_html_extracts_first_quote_correctly(self):
        result = self.parser.parse_html(self.html)
        first = result[0]
        self.assertEqual(first["name"], "Albert Einstein")
        self.assertIn("world as we have created it", first["message"])

    # 4: все авторы и тексты непустые
    def test_parse_html_all_records_have_name_and_message(self):
        result = self.parser.parse_html(self.html)
        for item in result:
            with self.subTest(id=item["id"]):
                self.assertTrue(item["name"])
                self.assertTrue(item["message"])


class TestForumParserEdgeCases(unittest.TestCase):
    """
    Крайние случаи. HTML передаётся inline, чтобы не раздувать фикстуру
    искусственными блоками и не привязывать тесты к её содержимому.
    """

    def setUp(self):
        self.parser = ForumParser.for_quotes_toscrape()

    # 5: битый блок без автора пропускается
    def test_parse_html_skips_block_without_author(self):
        html = """
        <div class="quote">
          <span class="text">Valid quote</span>
          <small class="author">Valid Author</small>
        </div>
        <div class="quote">
          <span class="text">Broken quote without author</span>
        </div>
        """
        result = self.parser.parse_html(html)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Valid Author")

    # 6: пустая страница даёт пустой список
    def test_parse_html_empty_page_returns_empty_list(self):
        result = self.parser.parse_html("<html><body></body></html>")
        self.assertEqual(result, [])


class TestForumParserSaveToDb(unittest.TestCase):

    def setUp(self):
        self.repo = DatabaseRepository(":memory:")
        self.addCleanup(self.repo.close)
        self.parser = ForumParser.for_quotes_toscrape()
        self.html = (FIXTURES / "quotes_page.html").read_text(encoding="utf-8")

    # 7: сохранение всех извлечённых записей
    def test_save_to_db_inserts_all_parsed_records(self):
        parsed = self.parser.parse_html(self.html)
        saved = self.parser.save_to_db(parsed, self.repo)

        self.assertEqual(saved, 10)
        self.assertEqual(self.repo.get_by_id(1)["name"], "Albert Einstein")
        self.assertEqual(self.repo.get_by_id(2)["name"], "J.K. Rowling")

    # 8: повторное сохранение не дублирует записи
    def test_save_to_db_skips_duplicates(self):
        parsed = self.parser.parse_html(self.html)
        first = self.parser.save_to_db(parsed, self.repo)
        second = self.parser.save_to_db(parsed, self.repo)

        self.assertEqual(first, 10)
        self.assertEqual(second, 0)
        # у Albert Einstein на первой странице 3 цитаты
        self.assertEqual(len(self.repo.get_by_name("Albert Einstein")), 3)