import json

# Input file (your cleaned logdocs.json)
with open("logdocs.json", "r") as f:
    data = json.load(f)

log_dict = {}

for entry in data:
    field = entry.get("col_0", "").strip()
    if not field:
        continue
    log_dict[field] = {
        "unit": entry.get("col_1", "").strip(),
        "description": entry.get("col_2", "").strip()
    }

# Output file
with open("logdocs_dict.json", "w") as f:
    json.dump(log_dict, f, indent=2)

print(f"[✔] Converted to dictionary format with {len(log_dict)} fields.")
