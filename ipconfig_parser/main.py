from pathlib import Path
import json
import re

# többértékű mezők
MULTI_VALUE_KEYS = {"dns_servers", "default_gateway"}

# adapter felismerés
ADAPTER_RE = re.compile(r"^(.*adapter.*?):\s*$", re.IGNORECASE)


def clean(key):
    return re.sub(r"\.+", "", key.lower()).strip()


def parse_ipconfig(file_path):
    adapters = []
    current = None
    last_key = None

    for line in Path(file_path).read_text(encoding="utf-16").splitlines():
        line = line.strip()

        # header kihagyás
        if not line or line.startswith("Windows IP Configuration"):
            continue

        # adapter detect
        match = ADAPTER_RE.match(line)
        if match:
            if current:
                adapters.append(current)

            current = {
                "adapter_name": match.group(1).strip()
            }
            last_key = None
            continue

        if not current:
            continue

        # key-value sor
        if ":" in line:
            k, v = line.split(":", 1)
            key = clean(k).replace(" ", "_")
            value = v.strip()

            if key in MULTI_VALUE_KEYS:
                parsed = value.split() if value else []
            else:
                parsed = value if value else ""

            current[key] = parsed
            

            last_key = key

        # folytató sor (pl DNS több sorban)
        elif last_key:
            extra = line.strip()
            if not extra:
                continue

            if last_key in MULTI_VALUE_KEYS:
                current[last_key] = current[last_key] + extra.split()
            else:
                if current[last_key] == "":
                    current[last_key] = extra
                else:
                    current[last_key] += " " + extra

    if current:
        adapters.append(current)

    # biztosítás: minden multi mező lista legyen
    for adapter in adapters:
        for key in MULTI_VALUE_KEYS:
            if key in adapter:
                if isinstance(adapter[key], str):
                    adapter[key] = [adapter[key]] if adapter[key] else []
                elif adapter[key] is None:
                    adapter[key] = []

    return adapters


def main():
    for path in sorted(Path(".").glob("*.txt")):
        output = {
            "file_name": path.name,
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