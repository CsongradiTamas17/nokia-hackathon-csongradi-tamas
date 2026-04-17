from math import comb
from pathlib import Path

def min_num_of_drops(N, H):
    if H == 0:
        return 0
    
    # Próbák száma
    m = 0

    while True:
        m += 1

        # Kiszámoljuk, hány szintet tudunk tesztelni m próbával
        total = 0
        for i in range(1, N + 1):
            total += comb(m, i)
            if total >= H:
                break

        if total >= H:
            return m

def main():
    data = Path("input.txt").read_text(encoding="utf-8").strip().splitlines()

    for line in data:
        line = line.strip()
        if not line:
            continue
        
        # Adatok
        parts = line.split(",")
        if len(parts) != 2:
            continue
        
        N, H = map(int, parts)

        result = min_num_of_drops(N, H)
        print(result)


if __name__ == "__main__":
    main()
