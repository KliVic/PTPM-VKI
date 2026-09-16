import logging
import os
import unittest

# Создаём папку под логи тестов
os.makedirs("tests/logs", exist_ok=True)


#Перенастраиваем логгер: force=True сносит старые обработчики
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | [%(levelname)-7s] | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("tests/logs/test_run.log", encoding="utf-8"),
    ],
    force=True,
)

logging.info("Логирование тестов перенастроено на tests/logs/test_run.log")

import validation as validation
from validation import (
    validate_login,
    validate_password,
    validate_credentials,
    mask,
)


class TestValidateLogin(unittest.TestCase):

    def setUp(self):
        # чистим "базу" зарегистрированных пользователей перед каждым тестом
        validation.registered_users.clear()

    # --- валидные логины ---

    def test_valid_phone(self):
        ok, msg = validate_login("+7-999-123-4567")
        self.assertTrue(ok, msg)
        self.assertEqual(msg, "")

    def test_valid_email(self):
        ok, msg = validate_login("user@example.com")
        self.assertTrue(ok, msg)
        self.assertEqual(msg, "")

    def test_valid_string_login(self):
        ok, msg = validate_login("user_01")
        self.assertTrue(ok, msg)
        self.assertEqual(msg, "")

    def test_valid_string_login_min_length(self):
        # ровно 5 символов — граница
        ok, msg = validate_login("abcde")
        self.assertTrue(ok, msg)

    # --- инвалидные логины ---

    def test_empty_login(self):
        ok, msg = validate_login("")
        self.assertFalse(ok)
        self.assertEqual(msg, "Логин не указан")

    def test_bad_phone_wrong_separator(self):
        ok, msg = validate_login("+7 999 123 4567")
        self.assertFalse(ok)
        self.assertIn("телефон", msg.lower())

    def test_bad_phone_missing_digit(self):
        ok, msg = validate_login("+7-99-123-4567")
        self.assertFalse(ok)

    def test_bad_email_no_dot(self):
        ok, msg = validate_login("user@example")
        self.assertFalse(ok)
        self.assertIn("email", msg.lower())

    def test_bad_email_double_at(self):
        ok, msg = validate_login("a@@b.com")
        self.assertFalse(ok)

    def test_string_login_too_short(self):
        ok, msg = validate_login("abcd")
        self.assertFalse(ok)
        self.assertIn("5", msg)

    def test_string_login_forbidden_chars(self):
        ok, msg = validate_login("user-name")
        self.assertFalse(ok)
        self.assertIn("латиниц", msg.lower())

    def test_string_login_cyrillic_rejected(self):
        ok, msg = validate_login("пользователь")
        self.assertFalse(ok)

    def test_blacklisted_login(self):
        ok, msg = validate_login("admin")
        self.assertFalse(ok)
        self.assertIn("черн", msg.lower())

    def test_blacklisted_login_case_insensitive(self):
        ok, msg = validate_login("ADMIN")
        self.assertFalse(ok)

    def test_already_registered_login(self):
        validation.registered_users["user_01"] = "Какой-тоПароль1!"
        ok, msg = validate_login("user_01")
        self.assertFalse(ok)
        self.assertIn("зарегистр", msg.lower())


class TestValidatePassword(unittest.TestCase):

    def test_valid_password(self):
        ok, msg = validate_password("Пароль1!", "Пароль1!")
        self.assertTrue(ok, msg)
        self.assertEqual(msg, "")

    def test_valid_password_min_length(self):
        ok, msg = validate_password("Аб1!абв", "Аб1!абв")
        self.assertTrue(ok, msg)

    def test_empty_password(self):
        ok, msg = validate_password("", "")
        self.assertFalse(ok)
        self.assertEqual(msg, "Пароль не указан")

    def test_password_too_short(self):
        ok, msg = validate_password("П1!абв", "П1!абв")
        self.assertFalse(ok)
        self.assertIn("7", msg)

    def test_password_no_upper(self):
        ok, msg = validate_password("пароль1!", "пароль1!")
        self.assertFalse(ok)
        self.assertIn("заглавн", msg.lower())

    def test_password_no_lower(self):
        ok, msg = validate_password("ПАРОЛЬ1!", "ПАРОЛЬ1!")
        self.assertFalse(ok)
        self.assertIn("строчн", msg.lower())

    def test_password_no_digit(self):
        ok, msg = validate_password("Пароль!", "Пароль!")
        self.assertFalse(ok)
        self.assertIn("цифр", msg.lower())

    def test_password_no_special(self):
        ok, msg = validate_password("Пароль1", "Пароль1")
        self.assertFalse(ok)
        self.assertIn("спецсимвол", msg.lower())

    def test_password_latin_rejected(self):
        ok, msg = validate_password("Password1!", "Password1!")
        self.assertFalse(ok)
        self.assertIn("кириллиц", msg.lower())

    def test_empty_confirm(self):
        ok, msg = validate_password("Пароль1!", "")
        self.assertFalse(ok)
        self.assertIn("подтвержд", msg.lower())

    def test_passwords_do_not_match(self):
        ok, msg = validate_password("Пароль1!", "Пароль2!")
        self.assertFalse(ok)
        self.assertIn("не совпада", msg.lower())


class TestValidateCredentials(unittest.TestCase):

    def setUp(self):
        validation.registered_users.clear()

    def test_full_success(self):
        ok, msg = validate_credentials("user_01", "Пароль1!", "Пароль1!")
        self.assertTrue(ok, msg)

    def test_full_success_via_phone(self):
        ok, msg = validate_credentials("+7-999-123-4567", "Пароль1!", "Пароль1!")
        self.assertTrue(ok, msg)

    def test_full_success_via_email(self):
        ok, msg = validate_credentials("u@e.com", "Пароль1!", "Пароль1!")
        self.assertTrue(ok, msg)

    def test_login_fails_first(self):
        # и логин плохой, и пароль плохой — должна вернуться ошибка логина
        ok, msg = validate_credentials("ab", "короткий", "короткий")
        self.assertFalse(ok)
        self.assertIn("5", msg)

    def test_password_fails_second(self):
        # логин валидный, пароль — нет
        ok, msg = validate_credentials("user_01", "плохой", "плохой")
        self.assertFalse(ok)
        self.assertIn("7", msg)

    def test_confirm_mismatch(self):
        ok, msg = validate_credentials("user_01", "Пароль1!", "Пароль2!")
        self.assertFalse(ok)
        self.assertIn("не совпада", msg.lower())


class TestMask(unittest.TestCase):

    def test_mask_hides_length(self):
        self.assertEqual(mask(""), "")
        self.assertEqual(mask("1234"), "****")
        self.assertEqual(mask("Пароль1!"), "********")

    def test_mask_does_not_reveal_content(self):
        masked = mask("Секрет1!")
        self.assertNotIn("С", masked)
        self.assertNotIn("1", masked)


