from pathlib import Path

# Palindrom-szerű szám keresése
def next_magic_num(n: str) -> str:
    length = len(n)
    num = list(n)

    # Tükrözés
    for i in range(length // 2):
        num[-(i+1)]=num[i]
    
    mirrored_number = "".join(num)

    if mirrored_number > n:
        return mirrored_number
    
    num = list(mirrored_number)
    carry = 1
    mid = length // 2

    # Ha a szám páratlan hosszúságú, akkor növeljük a középső számot
    if length % 2 == 1:
        num[mid] = str(int(num[mid]) + 1)
        
        # Ha 9 volt és 10 lett, akkor vissza 0 és carry marad
        if num[mid] == '10':
            num[mid] = '0'
            carry = 1
        else:
            # Páros hossz esetén nincs középső szám, csak carry indul
            carry = 0
    else:
        carry = 1

    # Bal és jobb oldal indexek (szimmetrikus növeléshez)
    left = mid - 1 if length % 2 == 0 else mid - 1
    right = mid if length % 2 == 0 else mid + 1

    # Kifelé haladva növeljük a számot
    while left >= 0 and carry:
        new_digit = int(num[left]) + carry

        if new_digit == 10:
            num[left] = '0'
            num[right] = '0'
            carry = 1
        
        else:
            num[left] = str(new_digit)
            num[right] = str(new_digit)
            carry = 0
        
        left -= 1
        right += 1

    # Ha végig carry maradt (pl. 999 → 1001 eset)
    if carry:
        return "1" + ("0" * (length - 1)) + "1"

    return "".join(num)

# Szám ellenőrzése → inputok kezelésére használt (pl. 5^9)
def exponentiation(expr: str) -> int:
    if "^" in expr:
        a, b = expr.split("^")
        return int(a) ** int(b)
    return int(expr)

def main():
    data = Path("input.txt").read_text(encoding="utf-8").splitlines()

    for line in data:
        if not line.strip():
            continue

        number = str(exponentiation(line.strip()))
        print(next_magic_num(number))


if __name__ == "__main__":
    main()