import unittest

from appliances import build_breakdown, top_appliance,monthly_kwh

RATE = 0.325



class MonthlyKwhTests(unittest.TestCase):
    def test_fridge_running_all_day(self):
        self.assertAlmostEqual(monthly_kwh( 150, 24), 108.0)

    def test_laptop_five_hours_a_day(self):
        self.assertAlmostEqual(monthly_kwh( 60, 5), 9.0)
    def test_fractional_hours(self):
        self.assertAlmostEqual(monthly_kwh(10, 2.5), 0.75)
        
class BreakdownTests(unittest.TestCase):
    def test_ranking_is_most_to_least_expensive(self):
        appliances = [("Fridge", 150, 24), ("Laptop", 60, 5), ("Lamp", 10, 2)]
        names= [row["name"] for row in build_breakdown(appliances, RATE)]
        self.assertEqual(names, ["Fridge", "Laptop", "Lamp"])
    def test_cost_is_kwh_times_rate(self):
        breakdown = build_breakdown([("Fridge", 150, 24)], RATE)
        self.assertAlmostEqual(breakdown[0]["kwh"], 108.0)
        self.assertAlmostEqual(breakdown[0]["cost"], 35.10)
    def test_empty_list_gives_empty_breakdown(self):
        self.assertEqual(build_breakdown([], RATE), [])

class TopApplianceTests(unittest.TestCase):
    def test_fridge_is_top_with_its_share_of_the_bill(self):
        breakdown = build_breakdown(
            [("Fridge", 150, 24), ("Laptop", 60, 5)],
            RATE,
        )
        name, percent = top_appliance(breakdown, 119.00)
        self.assertEqual(name, "Fridge")
        self.assertEqual(round(percent, 2), 29.50)

    def test_top_appliance_found_even_if_list_not_sorted(self):
        rows = [{"name": "Lamp", "cost": 1.0}, {"name": "Heater", "cost": 9.0}]
        self.assertEqual(top_appliance(rows, 100)[0], "Heater")

    def test_no_appliances_gives_none(self):
        self.assertIsNone(top_appliance([], 119.00))


if __name__ == "__main__":
    unittest.main()
