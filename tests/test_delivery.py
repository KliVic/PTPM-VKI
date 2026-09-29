import unittest

from Delivery import calculate_delivery_cost


class TestDeliveryInputValidation(unittest.TestCase):

    # 1: неверные входные параметры возвращают (-1, '0000-00-00')
    def test_invalid_inputs_return_error(self):
        bad_cases = [
            (0.05, 100, "обычный"),
            (51.0, 100, "обычный"),
            (1.0, 0, "обычный"),
            (1.0, 5001, "обычный"),
            (1.0, 100, "жидкий"),
        ]
        for weight, distance, ptype in bad_cases:
            with self.subTest(weight=weight, distance=distance, ptype=ptype):
                cost, date = calculate_delivery_cost(weight, distance, ptype)
                self.assertEqual(cost, -1)
                self.assertEqual(date, "0000-00-00")


class TestDeliveryCostCalculation(unittest.TestCase):

    # 2: базовый тариф без надбавок
    def test_basic_cost_without_surcharges(self):
        cost, _ = calculate_delivery_cost(1.0, 100, "обычный")
        self.assertEqual(cost, 700)

    # 3: весовые надбавки за 5-20 кг и >=20 кг
    def test_weight_surcharges_applied(self):
        cases = [(10.0, 840), (25.0, 1050)]
        for weight, expected in cases:
            with self.subTest(weight=weight):
                cost, _ = calculate_delivery_cost(weight, 100, "обычный")
                self.assertEqual(cost, expected)

    # 4: надбавки за тип посылки
    def test_package_type_surcharges_applied(self):
        cases = [("хрупкий", 1000), ("опасный", 1700)]
        for ptype, expected in cases:
            with self.subTest(package_type=ptype):
                cost, _ = calculate_delivery_cost(1.0, 100, ptype)
                self.assertEqual(cost, expected)

    # 5: дата доставки зависит от расстояния
    def test_delivery_date_depends_on_distance(self):
        cases = [(100, "2026-09-04"), (1000, "2026-09-05"), (3000, "2026-09-09")]
        for distance, expected_date in cases:
            with self.subTest(distance=distance):
                _, date = calculate_delivery_cost(1.0, distance, "обычный")
                self.assertEqual(date, expected_date)


class TestDeliveryBugs(unittest.TestCase):

    # 6: экспресс должен стоить дороже обычной доставки
    @unittest.expectedFailure
    def test_express_should_cost_more_than_regular(self):
        express_cost, _ = calculate_delivery_cost(1.0, 100, "обычный", is_express=True)
        regular_cost, _ = calculate_delivery_cost(1.0, 100, "обычный", is_express=False)
        self.assertGreater(express_cost, regular_cost)

    # 7: экспресс не должен доставлять в день отправки
    @unittest.expectedFailure
    def test_express_should_not_deliver_same_day(self):
        _, date = calculate_delivery_cost(1.0, 100, "обычный", is_express=True)
        self.assertGreater(date, "2026-09-03")

    # 8: ровно 5.0 кг должно облагаться весовой надбавкой
    @unittest.expectedFailure
    def test_weight_5kg_boundary_should_get_surcharge(self):
        cost, _ = calculate_delivery_cost(5.0, 100, "обычный")
        self.assertEqual(cost, 840)

    # 9: стоимость должна округляться вверх, а не обрезаться
    @unittest.expectedFailure
    def test_cost_should_be_rounded_up_not_truncated(self):
        cost, _ = calculate_delivery_cost(25.0, 1, "обычный")
        self.assertEqual(cost, 308)

    # 10: нечисловой вес должен возвращать ошибку, а не падать
    def test_non_numeric_weight_raises_error(self):
        with self.assertRaises(TypeError):
            calculate_delivery_cost("5", 100, "обычный")