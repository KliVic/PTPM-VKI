import time
import unittest


class PrettyResult(unittest.TextTestResult):
    """Понятный построчный вывод: группа, номер, имя теста, статус, время."""

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self._counter = 0
        self._last_class = None
        self._start_run = None
        self._start_test = None

    def startTestRun(self):
        super().startTestRun()
        self._start_run = time.time()
        self.stream.writeln("")
        self.stream.writeln("=" * 60)
        self.stream.writeln("  ЗАПУСК ТЕСТОВ")
        self.stream.writeln("=" * 60)

    def startTest(self, test):
        super().startTest(test)
        cls = test.__class__.__name__
        if cls != self._last_class:
            self._last_class = cls
            self.stream.writeln("")
            self.stream.writeln("-" * 60)
            self.stream.writeln(f"  Группа: {cls}")
            self.stream.writeln("-" * 60)
        self._counter += 1
        self._start_test = time.time()
        self.stream.writeln("")
        self.stream.writeln(f"  [{self._counter:02d}] {test._testMethodName}")

    def _elapsed(self):
        if self._start_test is None:
            return ""
        return f" ({time.time() - self._start_test:.3f} c)"

    def addSuccess(self, test):
        super().addSuccess(test)
        self.stream.writeln(f"       OK{self._elapsed()}")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.stream.writeln(f"       ПРОВАЛ{self._elapsed()}")
        self.stream.writeln(f"       {err[1]}")

    def addError(self, test, err):
        super().addError(test, err)
        self.stream.writeln(f"       ОШИБКА{self._elapsed()}")
        self.stream.writeln(f"       {err[1]}")

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.stream.writeln(f"       ПРОПУЩЕН ({reason})")

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self.stream.writeln(f"       ОЖИДАЕМО УПАЛ (подтверждает баг){self._elapsed()}")

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self.stream.writeln("       НЕОЖИДАННО ПРОШЕЛ (проверь expectedFailure)")

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            kind = "ПРОВАЛ" if issubclass(err[0], test.failureException) else "ОШИБКА"
            self.stream.writeln(f"       {kind} в subTest: {subtest}")
            self.stream.writeln(f"       {err[1]}")

    def stopTestRun(self):
        super().stopTestRun()
        elapsed = time.time() - self._start_run
        total = self.testsRun
        failed = len(self.failures)
        errors = len(self.errors)
        skipped = len(self.skipped)
        exp_fail = len(self.expectedFailures)
        unexp_succ = len(self.unexpectedSuccesses)
        passed = total - failed - errors - skipped - exp_fail - unexp_succ

        self.stream.writeln("")
        self.stream.writeln("=" * 60)
        self.stream.writeln("  ИТОГИ")
        self.stream.writeln("=" * 60)
        self.stream.writeln(f"  Всего тестов      : {total}")
        self.stream.writeln(f"  Прошло успешно    : {passed}")
        self.stream.writeln(f"  Провалено         : {failed}")
        self.stream.writeln(f"  Ошибок            : {errors}")
        self.stream.writeln(f"  Пропущено         : {skipped}")
        self.stream.writeln(f"  Ожидаемо упало    : {exp_fail}")
        self.stream.writeln(f"  Неожиданно прошло : {unexp_succ}")
        self.stream.writeln(f"  Затрачено времени : {elapsed:.3f} c")
        self.stream.writeln("=" * 60)
        if failed == 0 and errors == 0 and unexp_succ == 0:
            self.stream.writeln("  РЕЗУЛЬТАТ: ВСЕ ХОРОШО")
        else:
            self.stream.writeln("  РЕЗУЛЬТАТ: ЕСТЬ ПРОБЛЕМЫ, СМОТРИ ВЫШЕ")
        self.stream.writeln("=" * 60)