"""Appliance running costs: monthly kWh, cost ranking, and the most expensive appliance."""

DAYS_IN_MONTH = 30


def monthly_kwh(watts, hours_per_day, days=DAYS_IN_MONTH):
    """Return the kWh an appliance uses in a month: watts x hours x days / 1000."""
    return watts * hours_per_day * days / 1000


def make_row(name, watts, hours_per_day, rate_per_kwh, days=DAYS_IN_MONTH):
    """Return one line of the breakdown as a dictionary."""
    kwh = monthly_kwh(watts, hours_per_day, days)
    return {
        "name": name,
        "watts": watts,
        "hours": hours_per_day,
        "kwh": kwh,
        "cost": kwh * rate_per_kwh,
    }


def cost_of(row):
    """Return the cost used to sort one breakdown row."""
    return row["cost"]


def build_breakdown(appliances, rate_per_kwh, days=DAYS_IN_MONTH):
    """Turn (name, watts, hours) tuples into rows sorted from most to least expensive."""
    rows = [
        make_row(name, watts, hours, rate_per_kwh, days)
        for name, watts, hours in appliances
    ]
    return sorted(rows, key=cost_of, reverse=True)


def top_appliance(breakdown, bill_total):
    """Return (name, percent of bill) for the costliest appliance, or None if there are none."""
    if len(breakdown) == 0:
        return None

    top = max(breakdown, key=cost_of)
    if bill_total == 0:
        return (top["name"], 0.0)

    return (top["name"], top["cost"] / bill_total * 100)