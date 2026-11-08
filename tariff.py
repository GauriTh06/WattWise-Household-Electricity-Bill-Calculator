TIER_1_LIMIT = 100
TIER_2_LIMIT = 100
TIER_1_RATE = 0.20
TIER_2_RATE = 0.30
TIER_3_RATE = 0.45  # everything above 200 kWh
STANDING_CHARGE_PER_DAY = 0.50
DAYS_IN_MONTH = 30


def calculate_consumption(previous, current):
    """Return the kWh used between two meter readings.

    Raises ValueError when a reading is negative or the meter seems to run
    backwards.
    """
    if previous < 0 or current < 0:
        raise ValueError("Meter readings cannot be negative.")
    if current < previous:
        raise ValueError(
            f"Current reading ({current:g}) is lower than previous reading "
            f"({previous:g}). Please check your meter readings."
        )
    return current - previous


def split_into_tiers(kwh):
    """Split a consumption figure into [tier 1 kWh, tier 2 kWh, tier 3 kWh]."""
    if kwh <= TIER_1_LIMIT:
        return [kwh, 0, 0]
    elif kwh <= TIER_1_LIMIT + TIER_2_LIMIT:
        return [TIER_1_LIMIT, kwh - TIER_1_LIMIT, 0]
    else:
        return [TIER_1_LIMIT, TIER_2_LIMIT, kwh - TIER_1_LIMIT - TIER_2_LIMIT]


def calculate_bill(kwh, days=DAYS_IN_MONTH):
    """Return a dictionary describing the full bill for this many kWh."""
    tiers = split_into_tiers(kwh)
    rates = [TIER_1_RATE, TIER_2_RATE, TIER_3_RATE]
    tier_costs = []
    for index in range(3):
        tier_costs.append(tiers[index] * rates[index])

    energy_charge = sum(tier_costs)
    standing_charge = days * STANDING_CHARGE_PER_DAY
    return {
        "kwh": kwh,
        "tiers": tiers,
        "rates": rates,
        "tier_costs": tier_costs,
        "energy_charge": energy_charge,
        "standing_charge": standing_charge,
        "days": days,
        "standing_rate": STANDING_CHARGE_PER_DAY,
        "total": round(energy_charge + standing_charge, 2),
    }


def average_rate(bill):
    """Average energy price per kWh on this bill (standing charge excluded)."""
    if bill["kwh"] == 0:
        return 0.0
    return bill["energy_charge"] / bill["kwh"]