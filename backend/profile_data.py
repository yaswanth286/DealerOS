import csv
from pathlib import Path
from collections import Counter
from decimal import Decimal, InvalidOperation

DATA_DIR = Path(__file__).parent / "data"

FILES = {
    "locations.csv": "location_id",
    "system_a.csv": "record_id",
    "system_b.csv": "entry_id",
}


def profile_csv(filename, key_column):
    path = DATA_DIR / filename

    print(f"\n{'=' * 55}")
    print(f"FILE: {filename}")
    print("=" * 55)

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        columns = reader.fieldnames or []

    print("Total rows:", len(rows))
    print("Columns:", columns)

    print("\nBlank values:")
    for column in columns:
        blanks = sum(
            1 for row in rows
            if not (row.get(column) or "").strip()
        )
        if blanks:
            print(f"  {column}: {blanks}")

    keys = [(row.get(key_column) or "").strip() for row in rows]
    duplicates = [
        key for key, count in Counter(keys).items()
        if key and count > 1
    ]
    print(f"\nDuplicate {key_column} values:", duplicates or "None")

    if "record_ref" in columns:
        print("\nUnusual references:")
        for row in rows:
            ref = (row.get("record_ref") or "").strip()
            if not ref.upper().startswith("REC-") or ref != ref.upper():
                print(" ", repr(ref))

        refs = [(row.get("record_ref") or "").strip() for row in rows]
        duplicates = [
            ref for ref, count in Counter(refs).items()
            if ref and count > 1
        ]
        print("\nDuplicate record_ref values:", duplicates or "None")

    for column in ("value", "total_value", "base_value", "adjustment"):
        if column in columns:
            print(f"\nInvalid or unusual {column} values:")
            found = False
            for row in rows:
                raw = (row.get(column) or "").strip()
                if not raw:
                    continue
                try:
                    Decimal(raw.replace(",", ""))
                except InvalidOperation:
                    print(" ", repr(raw))
                    found = True
            if not found:
                print("  None detected")


def main():
    for filename, key_column in FILES.items():
        profile_csv(filename, key_column)


if __name__ == "__main__":
    main()
