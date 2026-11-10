import unittest

from src.database import DatabaseRepository


class TestDatabaseRepository(unittest.TestCase):

    def setUp(self):
        self.repo = DatabaseRepository(":memory:")

    def tearDown(self):
        self.repo.close()

    #add

    # 1: успешное добавление
    def test_add_returns_true_and_record_is_retrievable(self):
        self.assertTrue(self.repo.add(1, "Alice", "Hello"))
        self.assertEqual(
            self.repo.get_by_id(1),
            {"id": 1, "name": "Alice", "message": "Hello"},
        )

    # 2: дублирование id вызывает ValueError
    def test_add_duplicate_id_raises_value_error(self):
        self.repo.add(1, "Alice", "Hello")
        with self.assertRaises(ValueError):
            self.repo.add(1, "Bob", "Another")

    # 3: слишком длинное name отклоняется
    def test_add_name_too_long_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.repo.add(1, "A" * 257, "Hello")

    # 4: слишком длинное message отклоняется
    def test_add_message_too_long_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.repo.add(1, "Alice", "x" * 8097)

    # 5: неверный тип id отклоняется
    def test_add_wrong_id_type_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.repo.add("1", "Alice", "Hello")

    #get_by_id

    # 6: возвращает запись по id
    def test_get_by_id_existing(self):
        self.repo.add(10, "Bob", "Hi there")
        self.assertEqual(
            self.repo.get_by_id(10),
            {"id": 10, "name": "Bob", "message": "Hi there"},
        )

    # 7: несуществующий id возвращает None
    def test_get_by_id_missing_returns_none(self):
        self.assertIsNone(self.repo.get_by_id(999))

    #get_by_name

    # 8: возвращает все записи пользователя
    def test_get_by_name_returns_all_user_comments(self):
        self.repo.add(1, "Alice", "First")
        self.repo.add(2, "Alice", "Second")
        self.repo.add(3, "Bob", "Other")

        result = self.repo.get_by_name("Alice")
        self.assertEqual(len(result), 2)
        self.assertEqual({r["id"] for r in result}, {1, 2})

    # 9: несуществующий пользователь — пустой список
    def test_get_by_name_missing_returns_empty_list(self):
        self.assertEqual(self.repo.get_by_name("Nobody"), [])

    #update

    # 10: успешное обновление существующей записи
    def test_update_existing_returns_true_and_changes_message(self):
        self.repo.add(1, "Alice", "Old")
        self.assertTrue(self.repo.update(1, "New"))
        self.assertEqual(self.repo.get_by_id(1)["message"], "New")

    # 11: обновление несуществующего id возвращает False
    def test_update_missing_returns_false(self):
        self.assertFalse(self.repo.update(999, "New"))

    # 12: слишком длинное новое сообщение отклоняется
    def test_update_message_too_long_raises_value_error(self):
        self.repo.add(1, "Alice", "Old")
        with self.assertRaises(ValueError):
            self.repo.update(1, "x" * 8097)

    #delete

    # 13: удаление существующей записи
    def test_delete_existing_returns_true_and_removes_record(self):
        self.repo.add(1, "Alice", "Hello")
        self.assertTrue(self.repo.delete(1))
        self.assertIsNone(self.repo.get_by_id(1))

    # 14: удаление несуществующей записи возвращает False
    def test_delete_missing_returns_false(self):
        self.assertFalse(self.repo.delete(999))