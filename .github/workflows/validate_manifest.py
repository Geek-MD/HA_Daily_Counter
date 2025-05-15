import json
import sys
import os

def validate_file(path, required_keys):
    if not os.path.exists(path):
        print(f"❌ {path} not found")
        sys.exit(1)

    try:
        with open(path) as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load {path}: {e}")
        sys.exit(1)

    missing = [k for k in required_keys if k not in data]
    if missing:
        print(f"❌ {path} is missing keys: {missing}")
        sys.exit(1)

    print(f"✅ {path} passed validation.")

if __name__ == "__main__":
    validate_file("custom_components/ha_daily_counter/manifest.json", ["domain", "name", "codeowners", "version"])
    validate_file("hacs.json", ["name", "content_in_root", "domains", "category"])
