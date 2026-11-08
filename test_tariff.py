import unittest

from tariff import average_rate, calculate_bill, calculate_consumption, split_into_tiers


class ConsumptionTests(unittest.TestCase):
    def test_consumption_is_current_minus_previous(self):
        self.assertEqual(calculate_consumption(1200, 1520), 320)

    def test_equal_readings_mean_zero_consumption(self):
        self.assertEqual(calculate_consumption(500, 500), 0)

    def test_reversed_readings_raise_a_clear_error(self):
        with self.assertRaises(ValueError) as caught:
            calculate_consumption(1520, 1200)

        self.assertIn("lower than previous", str(caught.exception))

    def test_negative_reading_is_rejected(self):
        with self.assertRaises(ValueError):
            calculate_consumption(-5, 100)


class TierTests(unittest.TestCase):
    def test_small_usage_stays_in_tier_one(self):
        self.assertEqual(split_into_tiers(80), [80, 0, 0])

    def test_exactly_100_fills_tier_one_only(self):
        self.assertEqual(split_into_tiers(100), [100, 0, 0])

    def test_exactly_200_fills_two_tiers(self):
        self.assertEqual(split_into_tiers(200), [100, 100, 0])

    def test_usage_above_200_reaches_tier_three(self):
        self.assertEqual(split_into_tiers(320), [100, 100, 120])


class BillTests(unittest.TestCase):
    def test_example_bill_is_119(self):
        # 100*0.20 + 100*0.30 + 120*0.45 + 30*0.50 = 119
        bill = calculate_bill(320)

        self.assertEqual(bill["total"], 119.00)
        self.assertAlmostEqual(bill["energy_charge"], 104.00)
        self.assertAlmostEqual(bill["standing_charge"], 15.00)

    def test_zero_usage_still_pays_standing_charge(self):
        self.assertEqual(calculate_bill(0)["total"], 15.00)

    def test_bill_at_tier_boundaries(self):
        self.assertEqual(calculate_bill(100)["total"], 35.00)  # 20 + 15
        self.assertEqual(calculate_bill(200)["total"], 65.00)  # 20 + 30 + 15

    def test_total_is_rounded_to_two_decimals(self):
        # 100*0.20 + 100*0.30 + 0.33*0.45 + 15 = 65.1485 -> 65.15
        self.assertEqual(calculate_bill(200.33)["total"], 65.15)

    def test_average_rate_excludes_standing_charge(self):
        self.assertAlmostEqual(average_rate(calculate_bill(320)), 0.325)

    def test_average_rate_is_zero_when_nothing_used(self):
        self.assertEqual(average_rate(calculate_bill(0)), 0.0)


if __name__ == "__main__":
    unittest.main()