from pathlib import Path
import json
import re

# csak ezeknél engedünk több értéket
MULTI_VALUE_KEYS = { "dns servers", "default gateway", }

def clean(key):
    return re.sub(r"\.+", "", key.lower()).strip()

# Adatok kezelése
def parse_value(key, value):
    value = value.strip()
    return value.split() if key in MULTI_VALUE_KEYS else value

def parse_ipconfig(file_path):
    adapters = []
    current = None
    last_key = None

    for line in Path(file_path).read_text(encoding="utf-16").splitlines():
        line = line.strip()
        low = line.lower()

        if "adapter" in low:
            if current:
                adapters.append(current)
            current = {"adapter_name": line.replace(":", "")}
            last_key = None
            continue

        if not current:
            continue

        if ":" in line:
            k, v = line.split(":", 1)
            key = clean(k)
            val = parse_value(key, v)

            current[key] = val
            last_key = key

        elif last_key:
            extra = parse_value(last_key, line)
            cur = current.get(last_key)

            if isinstance(cur, list):
                cur.extend(extra if isinstance(extra, list) else [extra])
            else:
                current[last_key] = f"{cur} {extra}" if isinstance(extra, str) else extra

    if current:
        adapters.append(current)

    return adapters

def main():
    for path in sorted(Path(".").glob("*.txt")):
        output = {
            "file_name": "ipconfig.log", # path.name
            "adapters": parse_ipconfig(path)
        }

        out_file = f"{path.stem}.json"
        Path(out_file).write_text(
            json.dumps(output, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        print(out_file)

if __name__ == "__main__":
    main()