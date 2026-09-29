import unittest


class PrettyResult(unittest.TextTestResult):
    """Понятный построчный вывод: [NN] имя_теста -> статус."""

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self._counter = 0
        self._last_class = None

    def startTest(self, test):
        super().startTest(test)
        cls = test.__class__.__name__
        if cls != self._last_class:
            self._last_class = cls
            self.stream.writeln("")
            self.stream.writeln("=" * 72)
            self.stream.writeln(f"  {cls}")
            self.stream.writeln("=" * 72)
        self._counter += 1
        self.stream.writeln("")
        self.stream.writeln(f"[{self._counter:02d}] {test._testMethodName}")

    def addSuccess(self, test):
        super().addSuccess(test)
        self.stream.writeln("     OK")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.stream.writeln("     FAIL")
        self.stream.writeln(f"     {err[1]}")

    def addError(self, test, err):
        super().addError(test, err)
        self.stream.writeln("     ERROR")
        self.stream.writeln(f"     {err[1]}")

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.stream.writeln(f"     SKIP ({reason})")

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self.stream.writeln("     EXPECTED FAILURE (документирует баг)")

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self.stream.writeln("     UNEXPECTED SUCCESS")