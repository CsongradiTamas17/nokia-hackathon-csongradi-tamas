from pathlib import Path
import json
import re

# többértékű mezők
MULTI_VALUE_KEYS = {"dns_servers", "default_gateway"}

# adapter felismerés
ADAPTER_RE = re.compile(r"^(.*adapter.*?):\s*$", re.IGNORECASE)

def clean(key):
    return re.sub(r"\.+", "", key.lower()).strip()

ALLOWED_KEYS = {
    "adapter_name",
    "description",
    "physical_address",
    "dhcp_enabled",
    "ipv4_address",
    "subnet_mask",
    "default_gateway",
    "dns_servers"
}

def empty_adapter(name):
    return {
        "adapter_name": name,
        "description": "",
        "physical_address": "",
        "dhcp_enabled": "",
        "ipv4_address": "",
        "subnet_mask": "",
        "default_gateway": [],
        "dns_servers": []
    }

def parse_ipconfig(file_path):
    adapters = []
    current = None
    last_key = None

    for line in Path(file_path).read_text(encoding="utf-16").splitlines():
        line = line.strip()

        if not line or line.startswith("Windows IP Configuration"):
            continue

        match = ADAPTER_RE.match(line)
        if match:
            if current:
                adapters.append(current)

            current = empty_adapter(match.group(1).strip())
            last_key = None
            continue

        if not current:
            continue

        if ":" in line:
            k, v = line.split(":", 1)
            key = clean(k).replace(" ", "_")
            value = v.strip()

            if key in ALLOWED_KEYS:
                if key in MULTI_VALUE_KEYS:
                    current[key] = value.split() if value else []
                else:
                    current[key] = value if value else ""

                last_key = key

        elif last_key:
            extra = line.strip()
            if not extra:
                continue

            if last_key in MULTI_VALUE_KEYS:
                current[last_key] += extra.split()
            else:
                if current[last_key] == "":
                    current[last_key] = extra
                else:
                    current[last_key] += " " + extra

    if current:
        adapters.append(current)

    return adapters


def main():
    for path in sorted(Path(".").glob("*.txt")):
        output = [
            {
                "file_name": path.name,
                "adapters": parse_ipconfig(path)
            }
        ]

        out_file = f"{path.stem}.json"

        Path(out_file).write_text(
            json.dumps(output, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        with open(out_file, "r", encoding="utf-8") as f:
            for line in f:
                print(line.strip("\n"))

if __name__ == "__main__":
    main()