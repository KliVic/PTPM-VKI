import logging
import unittest

# Заглушаем basicConfig, чтобы import validation не настроил логгер и не гадил в консоль
_original_basicConfig = logging.basicConfig
logging.basicConfig = lambda *a, **kw: None

from tests.reporter import PrettyResult  # noqa: E402

loader = unittest.TestLoader()
suite = loader.discover("tests", top_level_dir=".")

logging.basicConfig = _original_basicConfig
logging.disable(logging.CRITICAL)

print()
print("=" * 72)
print("  ЗАПУСК ТЕСТОВ")
print("=" * 72)

runner = unittest.TextTestRunner(resultclass=PrettyResult, verbosity=0)
result = runner.run(suite)

print()
print("=" * 72)
print(f"  Всего тестов:           {result.testsRun}")
print(f"  Успешно:                "
      f"{result.testsRun - len(result.failures) - len(result.errors) - len(result.expectedFailures)}")
print(f"  Провалено:              {len(result.failures)}")
print(f"  Ошибок:                 {len(result.errors)}")
print(f"  Ожидаемо провалено:     {len(result.expectedFailures)}")
print("=" * 72)