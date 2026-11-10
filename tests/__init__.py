import unittest

from .reporter import PrettyResult


_original_init = unittest.TextTestRunner.__init__


def _patched_init(self, *args, **kwargs):
    kwargs.setdefault("resultclass", PrettyResult)
    _original_init(self, *args, **kwargs)


unittest.TextTestRunner.__init__ = _patched_init