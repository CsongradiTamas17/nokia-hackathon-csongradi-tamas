from pathlib import Path
from datetime import datetime
import math
import re


def parse_time(s: str):
    return datetime.strptime(s.strip(), "%Y-%m-%d %H:%M:%S")

def calculate_fee(minutes):
    FREE_MINUTES = 30
    CHEAP_LIMIT_MINUTES = 3 * 60  # 3 óra
    CHEAP = 300
    EXPENSIVE_RATE = 500
    DAY = 24 * 60
    DAILY_CAP = 10000

    days = minutes // DAY
    rem = minutes % DAY

    cost = days * DAILY_CAP

    if rem <= FREE_MINUTES:
        return cost

    rem -= FREE_MINUTES

    cheap = min(rem, CHEAP_LIMIT_MINUTES)
    cost += math.ceil(cheap / 60) * CHEAP
    rem -= cheap

    if rem > 0:
        cost += math.ceil(rem / 60) * EXPENSIVE_RATE

    return cost

def main():
    data = Path("input.txt").read_text(encoding="utf-8").splitlines()
    
    for line in data:
        if not line.strip() or "RENDSZAM" in line or "=" in line:
            continue

        try:
            parts = re.split(r"\s{2,}|\t+", line.strip())

            plate = parts[0]
            entry = parse_time(parts[1])
            exit = parse_time(parts[2])

            # Ha a kilépés kisebb mint a belépés
            if exit < entry:
                print(f"{plate} → HIBA (kilépés korábbi)")
                continue

            minutes = int((exit - entry).total_seconds() // 60)
            fee = calculate_fee(minutes)

            print(f"{minutes} perc parkolás → {fee} forint")

        except Exception:
            print("HIBA a sor feldolgozásánál")

if __name__ == "__main__":
    main()
