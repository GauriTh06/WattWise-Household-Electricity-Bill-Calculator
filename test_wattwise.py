import io
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout

from wattwise import main, read_appliances, read_readings


class FileTestCase(unittest.TestCase):
    """Gives each test a temporary folder and a helper that writes a file into it."""

    def setUp(self):
        self.folder = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.folder)

    def write(self, name, text, encoding="utf-8"):
        path = os.path.join(self.folder, name)
        # newline="" keeps any \r\n in text exactly as written, like a Windows editor
        with open(path, "w", encoding=encoding, newline="") as file:
            file.write(text)
        return path

    def run_main(self, args):
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(args)
        return code, output.getvalue()


class ReadingFilesTests(FileTestCase):
    def test_reads_previous_and_current(self):
        path = self.write("r.txt", "# comment\nprevious = 1200\ncurrent = 1520\n")
        self.assertEqual(read_readings(path), (1200.0, 1520.0))

    def test_reads_windows_line_endings_and_bom(self):
        path = self.write(
            "r.txt",
            "previous = 1200\r\ncurrent = 1520\r\n",
            encoding="utf-8-sig",
        )
        self.assertEqual(read_readings(path), (1200.0, 1520.0))

    def test_missing_current_line_is_an_error(self):
        path = self.write("r.txt", "previous = 1200\n")
        with self.assertRaises(ValueError):
            read_readings(path)


class ApplianceFilesTests(FileTestCase):
    def test_reads_appliances_with_crlf_and_blank_lines(self):
        path = self.write("a.txt", "Fridge, 150, 24\r\n\r\nLaptop, 60, 5\r\n")
        self.assertEqual(
            read_appliances(path),
            [("Fridge", 150.0, 24.0), ("Laptop", 60.0, 5.0)],
        )

    def test_appliance_with_too_many_hours_is_rejected(self):
        path = self.write("a.txt", "Heater, 1000, 25\n")
        with self.assertRaises(ValueError):
            read_appliances(path)


class MainTests(FileTestCase):
    def setUp(self):
        super().setUp()
        self.appliances = self.write("a.txt", "Laptop, 60, 5\nFridge, 150, 24\n")

    def test_full_report_for_the_example(self):
        readings = self.write("r.txt", "previous = 1200\ncurrent = 1520\n")
        code, output = self.run_main([readings, self.appliances])

        self.assertEqual(code, 0)
        self.assertIn("Total consumption:     320.00 kWh", output)
        self.assertIn("Total bill: 119.00", output)
        self.assertIn(
            "Most expensive appliance: Fridge\n(29.50% of the total bill)",
            output,
        )

    def test_breakdown_lists_fridge_before_laptop(self):
        readings = self.write("r.txt", "previous = 1200\ncurrent = 1520\n")
        code, output = self.run_main([readings, self.appliances])

        self.assertLess(output.index("1     Fridge"), output.index("2     Laptop"))

    def test_reversed_readings_print_error_instead_of_crashing(self):
        readings = self.write("r.txt", "previous = 1520\ncurrent = 1200\n")
        code, output = self.run_main([readings, self.appliances])

        self.assertEqual(code, 1)
        self.assertIn(
            "Error: Current reading (1200) is lower than previous reading (1520)",
            output,
        )
        self.assertNotIn("Total bill", output)

    def test_non_number_reading_prints_error(self):
        readings = self.write("r.txt", "previous = abc\ncurrent = 1520\n")
        code, output = self.run_main([readings, self.appliances])

        self.assertEqual(code, 1)
        self.assertIn("'abc' is not a valid number", output)

    def test_missing_file_prints_error(self):
        missing = os.path.join(self.folder, "nope.txt")
        code, output = self.run_main([missing, self.appliances])

        self.assertEqual(code, 1)
        self.assertIn("Error: cannot find the file", output)


if __name__ == "__main__":
    unittest.main()