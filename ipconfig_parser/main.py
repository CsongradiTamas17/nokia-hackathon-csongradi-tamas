from pathlib import Path
import json
import re

# többértékű mezők
MULTI_VALUE_KEYS = {"dns_servers", "default_gateway"}

# adapter felismerés
ADAPTER_RE = re.compile(r"^(.*adapter.*?):\s*$", re.IGNORECASE)

GLOBAL_KEYS = {
    "host_name": "host_name",
    "primary_dns_suffix": "primary_dns_suffix",
    "node_type": "node_type",
    "ip_routing_enabled": "ip_routing_enabled",
    "wins_proxy_enabled": "wins_proxy_enabled",
    "dns_suffix_search_list": "dns_suffix_search_list"
}

def clean(key):
    return re.sub(r"\.+", "", key.lower()).strip()

def parse_ipconfig(file_path):
    adapters = []

    # HOST LISTA
    host = [{
        "host_name": "",
        "primary_dns_suffix": "",
        "node_type": "",
        "ip_routing_enabled": "",
        "wins_proxy_enabled": "",
        "dns_suffix_search_list": ""
    }]

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

            current = {
                "adapter_name": match.group(1).strip()
            }
            last_key = None
            continue

        if ":" in line:
            k, v = line.split(":", 1)
            key = clean(k).replace(" ", "_")
            value = v.strip()

            # HOST mezők
            if key in GLOBAL_KEYS:
                host[0][GLOBAL_KEYS[key]] = value if value else ""

            if not current:
                continue

            if key in MULTI_VALUE_KEYS:
                parsed = value.split() if value else []
            else:
                parsed = value if value else ""

            current[key] = parsed
            last_key = key

        elif last_key and current:
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

    # lista biztosítás
    for adapter in adapters:
        for key in MULTI_VALUE_KEYS:
            if key in adapter:
                if isinstance(adapter[key], str):
                    adapter[key] = [adapter[key]] if adapter[key] else []
                elif adapter[key] is None:
                    adapter[key] = []

    return host, adapters


def main():
    for path in sorted(Path(".").glob("*.txt")):
        host, adapters = parse_ipconfig(path)

        output = {
            "file_name": path.name,
            "host": host,
            "adapters": adapters
        }

        out_file = f"{path.stem}.json"

        Path(out_file).write_text(
            json.dumps(output, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        print(f"\n=== {out_file} ===")
        with open(out_file, "r", encoding="utf-8") as f:
            for line in f:
                print(line.rstrip("\n"))

if __name__ == "__main__":
    main()