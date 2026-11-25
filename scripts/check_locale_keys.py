#!/usr/bin/env python3
"""Check that locale catalogs share the same keys, array lengths, and placeholders."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCALES = ROOT / "locales"
REQUIRED = ("en", "zh", "es")


def leaves(obj, prefix=""):
    found = {}
    if isinstance(obj, dict):
        for key, value in obj.items():
            path = f"{prefix}.{key}" if prefix else key
            found.update(leaves(value, path))
    elif isinstance(obj, list):
        found[prefix] = ("list", len(obj))
        for index, value in enumerate(obj):
            found.update(leaves(value, f"{prefix}[{index}]"))
    else:
        found[prefix] = ("value", obj)
    return found


def placeholders(value):
    if not isinstance(value, str):
        return ()
    return tuple(re.findall(r"\{[^{}]+\}", value))


def main():
    catalogs = {}
    for name in REQUIRED:
        path = LOCALES / f"{name}.json"
        catalogs[name] = leaves(json.loads(path.read_text(encoding="utf-8")))

    base = catalogs["en"]
    failed = False
    for name, catalog in catalogs.items():
        missing = sorted(set(base) - set(catalog))
        extra = sorted(set(catalog) - set(base))
        if missing or extra:
            failed = True
            print(f"{name}: missing {missing} extra {extra}")

    for key, (kind, value) in base.items():
        for name, catalog in catalogs.items():
            other_kind, other = catalog[key]
            if kind != other_kind:
                failed = True
                print(f"{key}: {name} kind {other_kind} != en {kind}")
                continue
            if kind == "list" and value != other:
                failed = True
                print(f"{key}: {name} length {other} != en {value}")
            if kind == "value" and placeholders(value) != placeholders(other):
                failed = True
                print(
                    f"{key}: {name} placeholders {placeholders(other)} "
                    f"!= en {placeholders(value)}"
                )

    if failed:
        return 1
    print(f"locale key parity ok ({len(base)} leaves across {', '.join(REQUIRED)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
