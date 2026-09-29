import unittest

import main as validation
from main import (
    validate_login,
    validate_password,
    validate_credentials,
    mask,
)

class TestValidateLogin(unittest.TestCase):

    def setUp(self):
        validation.registered_users.clear()

    # 1: валидный телефон принимается
    def test_valid_phone_is_accepted(self):
        ok, msg = validate_login("+7-999-123-4567")
        self.assertTrue(ok, msg)
        self.assertEqual(msg, "")

    # 2: валидный email принимается
    def test_valid_email_is_accepted(self):
        ok, msg = validate_login("user@example.com")
        self.assertTrue(ok, msg)
        self.assertEqual(msg, "")

    # 3: валидный строковый логин граничной длины принимается
    def test_valid_string_login_is_accepted(self):
        ok, msg = validate_login("abcde")
        self.assertTrue(ok, msg)
        self.assertEqual(msg, "")

    # 4: пустой логин отклоняется
    def test_empty_login_returns_error(self):
        ok, msg = validate_login("")
        self.assertFalse(ok)
        self.assertEqual(msg, "Логин не указан")

    # 5: неверные форматы телефона отклоняются
    def test_phone_with_wrong_format_returns_error(self):
        bad_phones = ["+7 999 123 4567", "+7-99-123-4567", "+7-999-12-4567"]
        for phone in bad_phones:
            with self.subTest(phone=phone):
                ok, msg = validate_login(phone)
                self.assertFalse(ok)
                self.assertIn("телефон", msg.lower())

    # 6: неверные форматы email отклоняются
    def test_email_with_wrong_format_returns_error(self):
        bad_emails = ["user@example", "a@@b.com"]
        for email in bad_emails:
            with self.subTest(email=email):
                ok, msg = validate_login(email)
                self.assertFalse(ok)
                self.assertIn("email", msg.lower())

    # 7: слишком короткий логин-строка отклоняется
    def test_string_login_too_short_returns_error(self):
        ok, msg = validate_login("abcd")
        self.assertFalse(ok)
        self.assertIn("5", msg)

    # 8: логин-строка с недопустимыми символами отклоняется
    def test_string_login_with_forbidden_chars_returns_error(self):
        ok, msg = validate_login("user-name")
        self.assertFalse(ok)
        self.assertIn("латиниц", msg.lower())

    # 9: логины из чёрного списка отклоняются (регистр не важен)
    def test_blacklisted_login_returns_error(self):
        for login in ("admin", "ADMIN", "support"):
            with self.subTest(login=login):
                ok, msg = validate_login(login)
                self.assertFalse(ok)
                self.assertIn("черн", msg.lower())

    # 10: уже зарегистрированный логин отклоняется
    def test_already_registered_login_returns_error(self):
        validation.registered_users["user_01"] = "Пароль1!"
        ok, msg = validate_login("user_01")
        self.assertFalse(ok)
        self.assertIn("зарегистр", msg.lower())


class TestValidatePassword(unittest.TestCase):

    # 11: валидный пароль принимается
    def test_valid_password_is_accepted(self):
        ok, msg = validate_password("Аб1!абв", "Аб1!абв")
        self.assertTrue(ok, msg)
        self.assertEqual(msg, "")

    # 12: пустой пароль отклоняется
    def test_empty_password_returns_error(self):
        ok, msg = validate_password("", "")
        self.assertFalse(ok)
        self.assertEqual(msg, "Пароль не указан")

    # 13: слишком короткий пароль отклоняется
    def test_password_too_short_returns_error(self):
        ok, msg = validate_password("П1!абв", "П1!абв")
        self.assertFalse(ok)
        self.assertIn("7", msg)

    # 14: отсутствие одной из буквенных категорий регистра отклоняется
    def test_password_missing_case_returns_error(self):
        cases = [("пароль1!", "заглавн"), ("ПАРОЛЬ1!", "строчн")]
        for pwd, fragment in cases:
            with self.subTest(password=pwd):
                ok, msg = validate_password(pwd, pwd)
                self.assertFalse(ok)
                self.assertIn(fragment, msg.lower())

    # 15: пароль без цифры отклоняется
    def test_password_without_digit_returns_error(self):
        ok, msg = validate_password("Пароль!", "Пароль!")
        self.assertFalse(ok)
        self.assertIn("цифр", msg.lower())

    # 16: пароль без спецсимвола отклоняется
    def test_password_without_special_returns_error(self):
        ok, msg = validate_password("Пароль1", "Пароль1")
        self.assertFalse(ok)
        self.assertIn("спецсимвол", msg.lower())

    # 17: пароль с латиницей отклоняется
    def test_password_with_latin_returns_error(self):
        ok, msg = validate_password("Password1!", "Password1!")
        self.assertFalse(ok)
        self.assertIn("кириллиц", msg.lower())

    # 18: несовпадение пароля и подтверждения отклоняется
    def test_passwords_do_not_match_returns_error(self):
        ok, msg = validate_password("Пароль1!", "Пароль2!")
        self.assertFalse(ok)
        self.assertIn("не совпада", msg.lower())


class TestValidateCredentials(unittest.TestCase):

    def setUp(self):
        validation.registered_users.clear()

    # 19: валидные данные для трёх типов логина принимаются
    def test_all_credentials_valid_returns_success(self):
        logins = ["user_01", "+7-999-123-4567", "u@e.com"]
        for login in logins:
            with self.subTest(login=login):
                ok, msg = validate_credentials(login, "Пароль1!", "Пароль1!")
                self.assertTrue(ok, msg)


class TestMask(unittest.TestCase):

    # 20: маска сохраняет длину и скрывает содержимое
    def test_mask_preserves_length_and_hides_content(self):
        self.assertEqual(mask(""), "")
        self.assertEqual(mask("1234"), "****")
        masked = mask("Пароль1!")
        self.assertEqual(masked, "********")
        self.assertNotIn("П", masked)
        self.assertNotIn("1", masked)