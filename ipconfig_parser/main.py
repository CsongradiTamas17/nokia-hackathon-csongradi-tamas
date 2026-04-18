from pathlib import Path
import json
import re

# csak ezeknél engedünk több értéket
MULTI_VALUE_KEYS = {
    "dns servers",
    "default gateway",
}

def read_file_safely(file_path):
    for enc in ["utf-8", "utf-16", "cp1250"]:
        try:
            with open(file_path, encoding=enc) as f:
                return f.readlines()
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Nem olvasható fájl: {file_path}")


def clean_key(key: str) -> str:
    key = key.lower()
    key = re.sub(r"\.+", "", key)
    return key.strip()

# Adatok kezelése
def parse_value(key: str, value: str):
    value = value.strip()

    if key in MULTI_VALUE_KEYS:
        return [v for v in value.split() if v]

    # minden más marad egyben (pl. dátumok)
    return value


def parse_ipconfig(file_path):
    lines = read_file_safely(file_path)

    adapters = []
    current = None
    last_key = None

    for line in lines:
        line = line.rstrip()

        # Új adapter
        if line.lower().startswith("ethernet adapter") or line.lower().startswith("wireless lan adapter"):
            if current:
                adapters.append(current)

            current = {
                "adapter_name": line.replace(":", "").strip(),
            }

            last_key = None
            continue

        if not current:
            continue

        if ":" in line:
            key_part, value_part = line.split(":", 1)

            key = clean_key(key_part)
            value = value_part.strip()

            last_key = key

            parsed = parse_value(key, value)

            current[key] = parsed

        else:
            extra = line.strip()
            if not extra or not last_key:
                continue

            parsed = parse_value(last_key, extra)

            existing = current.get(last_key)

            if isinstance(existing, list):
                current[last_key].extend(parsed if isinstance(parsed, list) else [parsed])
            elif isinstance(existing, str):
                current[last_key] = existing + " " + parsed if isinstance(parsed, str) else existing
            else:
                current[last_key] = parsed

    if current:
        adapters.append(current)

    return adapters


def main():
    for path in sorted(Path(".").glob("*.txt")):
        adapters = parse_ipconfig(path)

        output = {
            "file_name": path.name,
            "adapters": adapters
        }

        # Json fájlba írás (ami MULTI_VALUE_KEYS, az egy sorba íródjon)
        json_text = json.dumps(output, indent=2, ensure_ascii=False)

        for key in MULTI_VALUE_KEYS:
            pattern = rf'("{re.escape(key)}": )\[\n(.*?)\n\s*\]'

            json_text = re.sub(
                pattern,
                lambda m: m.group(1) + "[" +
                          ", ".join(f'"{x}"' for x in re.findall(r'"(.*?)"', m.group(2))) +
                          "]",
                json_text,
                flags=re.DOTALL
            )

        output_name = "output_" + path.stem + ".json"

        with open(output_name, "w", encoding="utf-8") as f:
            f.write(json_text)

        print(output_name)


if __name__ == "__main__":
    main()
