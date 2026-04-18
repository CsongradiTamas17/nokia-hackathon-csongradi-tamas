from pathlib import Path

def next_magic_num(n: str) -> str:
    length = len(n)
    num = list(n)

    for i in range(length // 2): # Tükrözés
        num[-i - 1] = num[i]
    
    if "".join(num) > n:
        return "".join(num)

    carry = 1
    left = (length - 1) // 2
    right = length // 2

    while left >= 0 and carry: # Középről kifelé növelés
        for i in (left, right):
            if i < 0 or i >= length:
                continue

        new = int(num[left]) + carry

        if new == 10:
            num[left] = num[right] = "0"
            carry = 1
        else:
            num[left] = num[right] = str(new)
            carry = 0

        left -= 1
        right += 1

    # overflow (999 -> 1001)
    return "1" + "0" * (length - 1) + "1" if carry else "".join(num)

def exponentiation(expr: str) -> int:   # Szám ellenőrzése (pl. 5^9)
    return eval(expr.replace("^", "**"))

def main():
    data = Path("input.txt").read_text(encoding="utf-8").splitlines()

    for line in data:
        if not line.strip():
            continue

        print(next_magic_num(str(exponentiation(line.strip()))))


if __name__ == "__main__":
    main()