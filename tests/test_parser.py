import unittest
from pathlib import Path

from src.database import DatabaseRepository
from src.parser import ForumParser

FIXTURE = Path(__file__).parent / "fixtures" / "forum_page.html"


class TestForumParser(unittest.TestCase):

    def setUp(self):
        self.parser = ForumParser()
        self.html = FIXTURE.read_text(encoding="utf-8")

    # 1: разбор корректной страницы из фикстуры
    def test_parse_html_extracts_all_valid_comments(self):
        result = self.parser.parse_html(self.html)

        self.assertEqual(len(result), 3)
        ids = [item["id"] for item in result]
        self.assertEqual(ids, [101, 102, 103])

        alice_first = result[0]
        self.assertEqual(alice_first["name"], "Alice")
        self.assertIn("<b>world</b>", alice_first["message"])

    # 2: битые блоки (без id, без автора, с нечисловым id) пропускаются
    def test_parse_html_skips_malformed_blocks(self):
        result = self.parser.parse_html(self.html)
        ids = {item["id"] for item in result}
        # 104 (без .username) и "abc" (нечисловой id) и безымянный
        # блок без data-id не должны попасть
        self.assertNotIn(104, ids)
        self.assertEqual(len(result), 3)

    # 3: сохранение в БД
    def test_save_to_db_inserts_all_parsed_records(self):
        repo = DatabaseRepository(":memory:")
        self.addCleanup(repo.close)

        parsed = self.parser.parse_html(self.html)
        saved = self.parser.save_to_db(parsed, repo)

        self.assertEqual(saved, 3)
        self.assertEqual(repo.get_by_id(101)["name"], "Alice")
        self.assertEqual(repo.get_by_id(102)["name"], "Bob")

    # 4: повторное сохранение не дублирует записи
    def test_save_to_db_skips_duplicates(self):
        repo = DatabaseRepository(":memory:")
        self.addCleanup(repo.close)

        parsed = self.parser.parse_html(self.html)
        first = self.parser.save_to_db(parsed, repo)
        second = self.parser.save_to_db(parsed, repo)

        self.assertEqual(first, 3)
        self.assertEqual(second, 0)
        self.assertEqual(len(repo.get_by_name("Alice")), 2)