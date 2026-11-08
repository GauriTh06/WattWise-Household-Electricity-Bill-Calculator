"""WattWise console app: reads meter readings and appliances, prints the bill and breakdown."""

import sys

from appliances import build_breakdown, top_appliance
from tariff import average_rate, calculate_bill, calculate_consumption


DEFAULT_READINGS = "readings.txt"
DEFAULT_APPLIANCES = "appliances.txt"


def useful_lines(path):
    """Lines of a text file with blanks and # comments removed (works for \n and \r\n)."""
    lines = []
    with open(path, encoding="utf-8-sig") as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):
                lines.append(line)
    return lines


def to_number(text, what):
    """Convert text to a float, or raise ValueError with a friendly message."""
    try:
        return float(text)
    except ValueError:
        raise ValueError(f"{text!r} is not a valid number for {what}.")


def read_readings(path):
    """Read 'previous = ...' and 'current = ...' lines and return (previous, current)."""
    readings = {}
    for line in useful_lines(path):
        if "=" not in line:
            raise ValueError(f"Readings line {line!r} should look like: previous = 1200")
        key, value = line.split("=", 1)
        key = key.strip().lower()
        readings[key] = to_number(value.strip(), f"the {key} reading")

    if "previous" not in readings or "current" not in readings:
        raise ValueError("The readings file needs both a 'previous' and a 'current' line.")

    return readings["previous"], readings["current"]


def read_appliances(path):
    """Read 'name, watts, hours' lines and return a list of (name, watts, hours) tuples."""
    appliances = []
    for line in useful_lines(path):
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 3:
            raise ValueError(f"Appliance line {line!r} should look like: Fridge, 150, 24")

        name = parts[0]
        watts = to_number(parts[1], f"{name} watts")
        hours = to_number(parts[2], f"{name} hours per day")

        if watts < 0:
            raise ValueError(f"{name} cannot use negative watts.")
        if hours < 0 or hours > 24:
            raise ValueError(f"{name} hours per day must be between 0 and 24.")

        appliances.append((name, watts, hours))

    return appliances


def print_bill(previous, current, bill):
    print("WattWise Bill Summary")
    print("=====================")
    print(f"Previous reading: {previous:10.2f} kWh")
    print(f"Current reading:  {current:10.2f} kWh")
    print(f"Total consumption: {bill['kwh']:10.2f} kWh")
    print()

    for index in range(3):
        kwh = bill["tiers"][index]
        rate = bill["rates"][index]
        cost = bill["tier_costs"][index]
        print(f"Tier {index + 1}: {kwh:7.2f} kWh x {rate:.2f} = {cost:7.2f}")

    days = bill["days"]
    standing_rate = bill["standing_rate"]
    print(f"Standing charge: {days} days x {standing_rate:.2f} = {bill['standing_charge']:.2f}")
    print("---------------------")
    print(f"Total bill: {bill['total']:.2f}")


def print_breakdown(breakdown, rate, bill_total):
    print()
    print("Appliance Cost Breakdown (most to least expensive)")
    print(f"Costs use your average energy rate of {rate:.4f} per kWh.")

    if len(breakdown) == 0:
        print("No appliances listed.")
        return

    print(f"{'Rank':<5} {'Appliance':<15} {'kWh/month':>10} {'Cost':>8}")
    rank = 1
    for row in breakdown:
        print(f"{rank:<5} {row['name']:<15} {row['kwh']:10.2f} {row['cost']:8.2f}")
        rank += 1

    name, percent = top_appliance(breakdown, bill_total)
    print()
    print(f"Most expensive appliance: {name}")
    print(f"({percent:.2f}% of the total bill)")


def main(args):
    """Run WattWise. args are optional [readings file, appliances file]. Returns an exit code."""
    readings_path = DEFAULT_READINGS
    appliances_path = DEFAULT_APPLIANCES
    if len(args) >= 1:
        readings_path = args[0]
    if len(args) >= 2:
        appliances_path = args[1]

    try:
        previous, current = read_readings(readings_path)
        kwh = calculate_consumption(previous, current)
        appliances = read_appliances(appliances_path)
    except FileNotFoundError as error:
        print(f"Error: cannot find the file '{error.filename}'.")
        return 1
    except ValueError as error:
        print(f"Error: {error}")
        return 1

    bill = calculate_bill(kwh)
    rate = average_rate(bill)
    breakdown = build_breakdown(appliances, rate)
    print_bill(previous, current, bill)
    print_breakdown(breakdown, rate, bill["total"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))