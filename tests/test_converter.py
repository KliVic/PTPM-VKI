import unittest

from converter import Converter

#  py -m unittest discover -s tests -t . -v

class TestConverterAboveUpperBoundary(unittest.TestCase):
    """Ветка x >= 100.7 -> 1000."""

    # 1: нижняя граница диапазона включена
    def test_x_at_lower_boundary_returns_1000(self):
        self.assertEqual(Converter.do(100.7), 1000)

    # 2: типичное значение в диапазоне
    def test_x_well_above_boundary_returns_1000(self):
        for x in (150.0, 500.0, 1000.0):
            with self.subTest(x=x):
                self.assertEqual(Converter.do(x), 1000)

    # 3: чуть ниже границы уже другая ветка
    def test_x_just_below_upper_boundary_returns_int_part(self):
        self.assertEqual(Converter.do(100.6), 100)


class TestConverterPositiveRange(unittest.TestCase):
    """Ветка 0 < x < 100.7 -> int(x)."""

    # 4: типичные положительные значения
    def test_positive_values_return_int_part(self):
        cases = [
            (0.1, 0),
            (0.9, 0),
            (1.0, 1),
            (50.5, 50),
            (99.9, 99),
            (100.0, 100),
        ]
        for x, expected in cases:
            with self.subTest(x=x):
                self.assertEqual(Converter.do(x), expected)


class TestConverterZero(unittest.TestCase):
    """Ветка x == 0.0 -> ValueError."""

    # 5: ровно 0.0 вызывает ValueError
    def test_zero_float_raises_value_error(self):
        with self.assertRaises(ValueError):
            Converter.do(0.0)

    # 6: целочисленный 0 тоже равен 0.0 тоже должен падать
    def test_zero_int_raises_value_error(self):
        with self.assertRaises(ValueError):
            Converter.do(0)


class TestConverterSmallNegativeRange(unittest.TestCase):
    """Ветка -30.4 <= x < 0 -> int(x) - 5."""

    # 7: типичные отрицательные значения
    def test_small_negative_values_return_int_minus_five(self):
        cases = [
            (-0.1, -5),    # int(-0.1) = 0
            (-0.9, -5),    # int(-0.9) = 0
            (-1.0, -6),    # int(-1.0) = -1, -1 - 5 = -6
            (-15.5, -20),  # int(-15.5) = -15, -15 - 5 = -20
            (-30.3, -35),  # int(-30.3) = -30, -30 - 5 = -35
        ]
        for x, expected in cases:
            with self.subTest(x=x):
                self.assertEqual(Converter.do(x), expected)

    # 8: нижняя граница диапазона включена
    def test_x_at_lower_boundary_returns_int_minus_five(self):
        self.assertEqual(Converter.do(-30.4), -35)   # int(-30.4) = -30, -30 - 5 = -35


class TestConverterFarNegativeRange(unittest.TestCase):
    """Ветка x <= -30.5 -> -2000."""

    # 9: верхняя граница диапазона включена
    def test_x_at_upper_boundary_returns_minus_2000(self):
        self.assertEqual(Converter.do(-30.5), -2000)

    # 10: глубоко отрицательные значения
    def test_far_negative_values_return_minus_2000(self):
        for x in (-30.6, -100.0, -1000.0):
            with self.subTest(x=x):
                self.assertEqual(Converter.do(x), -2000)


class TestConverterBoundariesMatrix(unittest.TestCase):
    """Полная карта границ — что происходит по обе стороны каждой границы."""

    # 11: все граничные значения сразу
    def test_all_boundaries(self):
        cases = [
            (100.8, 1000),
            (100.7, 1000),   # граница: включена сверху
            (100.6, 100),    # граница: уже в другой ветке
            (0.1, 0),
            (-0.1, -5),
            (-30.3, -35),
            (-30.4, -35),    # граница: включена снизу
            (-30.5, -2000),  # граница: уже в следующей ветке
            (-30.6, -2000),
        ]
        for x, expected in cases:
            with self.subTest(x=x):
                self.assertEqual(Converter.do(x), expected)

    # 12: возвращаемый тип int, а не float
    def test_return_type_is_int(self):
        for x in (150.0, 50.5, -0.1, -30.4, -30.5):
            with self.subTest(x=x):
                self.assertIsInstance(Converter.do(x), int)