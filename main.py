import logging
import os

# Настройка логирования
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | [%(levelname)-7s] | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),  # консоль
        logging.FileHandler("logs/file_txt.log", encoding="utf-8"),  # файл
    ],
)

logging.info("Логгер успешно сконфигурирован")
logging.info("Приложение запущено")

# Данные


# Черный список логинов
BLACKLIST = {
    "admin", "administrator", "root", "user", "test", "guest",
    "moderator", "support", "qwerty", "password", "12345", "manager",
}

# "База" зарегистрированных пользователей: логин -> пароль
# (в реальной системе хранился бы хеш, здесь просто для практики)
registered_users = {}

# Вспомогательные функции
def mask(value):
    """Простое маскирование пароля: показывает длину, скрывает содержимое."""
    return "*" * len(value)


def is_cyr_upper(ch):
    return ("А" <= ch <= "Я") or ch == "Ё"


def is_cyr_lower(ch):
    return ("а" <= ch <= "я") or ch == "ё"


def is_cyr_letter(ch):
    return is_cyr_upper(ch) or is_cyr_lower(ch)


# Валидация
def validate_login(login):
    if not login:
        return False, "Логин не указан"

    # Телефон +x-xxx-xxx-xxxx
    if login.startswith("+"):
        parts = login.split("-")
        if (len(parts) != 4 or not parts[0][1:].isdigit()
                or len(parts[0]) != 2
                or any(not p.isdigit() or len(p) != 3 for p in parts[1:])):
            return False, "Неверный формат телефона. Ожидается +x-xxx-xxx-xxxx"

    # Email
    elif "@" in login:
        if "." not in login.split("@")[-1] or login.count("@") != 1:
            return False, "Неверный формат email"
        local, domain = login.split("@")
        if not local or not domain:
            return False, "Неверный формат email"

    # Обычная строка
    else:
        if len(login) < 5:
            return False, "Логин-строка должен содержать минимум 5 символов"
        for ch in login:
            if not (ch.isascii() and (ch.isalnum() or ch == "_")):
                return False, ("Логин-строка может содержать только латиницу, "
                               "цифры и знак подчеркивания")

    # Черный список
    if login.lower() in BLACKLIST:
        return False, "Логин находится в черном списке"

    # Уже зарегистрирован
    if login in registered_users:
        return False, "Такой логин уже зарегистрирован"

    return True, ""


def validate_password(password, confirm):
    if not password:
        return False, "Пароль не указан"

    if len(password) < 7:
        return False, "Пароль должен содержать минимум 7 символов"

    digits = set("0123456789")
    specials = set("!@#$%^&*()_+-=[]{};:'\"\\|,.<>/?`~")

    has_upper = False
    has_lower = False
    has_digit = False
    has_special = False

    for ch in password:
        if ch.isdigit():
            has_digit = True
        elif ch in specials:
            has_special = True
        elif is_cyr_upper(ch):
            has_upper = True
        elif is_cyr_lower(ch):
            has_lower = True
        else:
            return False, ("Пароль может содержать только кириллицу, "
                           "цифры и спецсимволы")

    if not has_upper:
        return False, "Пароль должен содержать хотя бы одну заглавную букву кириллицы"
    if not has_lower:
        return False, "Пароль должен содержать хотя бы одну строчную букву кириллицы"
    if not has_digit:
        return False, "Пароль должен содержать хотя бы одну цифру"
    if not has_special:
        return False, "Пароль должен содержать хотя бы один спецсимвол"

    if not confirm:
        return False, "Подтверждение пароля не указано"

    if password != confirm:
        return False, "Пароль и подтверждение пароля не совпадают"

    return True, ""


def validate_credentials(login, password, confirm):
    ok, msg = validate_login(login)
    if not ok:
        return False, msg
    ok, msg = validate_password(password, confirm)
    if not ok:
        return False, msg
    return True, ""


# Основной цикл
print("Регистрация пользователей. Ctrl+C (или Esc в некоторых терминалах) — выход.\n")

while True:
    try:
        login = input("Логин: ").strip()
        password = input("Пароль: ")
        confirm = input("Подтверждение пароля: ")

        masked_pass = mask(password)
        masked_conf = mask(confirm)

        logging.debug("Входные данные: login=%r, password=%s, confirm=%s",
                      login, masked_pass, masked_conf)

        try:
            success, message = validate_credentials(login, password, confirm)

            if success:
                registered_users[login] = password
                logging.info(
                    "Успешный запрос. login=%r, password=%s, confirm=%s. "
                    "Результат: True. Сообщение: ''",
                    login, masked_pass, masked_conf,
                )
            else:
                logging.error(
                    "Неуспешный запрос. login=%r, password=%s, confirm=%s. "
                    "Результат: False. Ошибка: %s",
                    login, masked_pass, masked_conf, message,
                )

            print("Результат:", success)
            print("Сообщение:", message if message else "(пусто)")
            print(f"Всего зарегистрировано: {len(registered_users)}")
            print("-" * 40)

        except Exception as ex:
            logging.exception(
                "Неуспешный запрос. login=%r, password=%s, confirm=%s. "
                "Исключение: %s",
                login, masked_pass, masked_conf, ex,
            )
            print("Результат: False")
            print(f"Внутренняя ошибка: {ex}")
            print("-" * 40)

    except (KeyboardInterrupt, EOFError):
        print("\nВыход из программы.")
        logging.info("Приложение остановлено пользователем")
        break