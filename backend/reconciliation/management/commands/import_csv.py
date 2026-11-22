
import csv
import re
from pathlib import Path
from decimal import Decimal, InvalidOperation
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from reconciliation.models import (
    Location,
    SystemARecord,
    SystemBEntry,
)


def parse_decimal(raw_value):
    """Convert a CSV amount into Decimal without replacing invalid data with zero."""
    if raw_value is None or not raw_value.strip():
        return None

    cleaned = raw_value.strip().replace(",", "")

    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def parse_date(raw_value):
    """Parse supported date formats. Preserve the original separately."""
    if raw_value is None or not raw_value.strip():
        return None

    value = raw_value.strip()

    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
    ]

    for date_format in formats:
        try:
            return datetime.strptime(value, date_format).date()
        except ValueError:
            continue

    return None


def normalize_ref(raw_value):
    """
    Normalize references such as:
    rec1034   -> REC-1034
    REC - 1070 -> REC-1070
    1112      -> REC-1112
    """
    if not raw_value or not raw_value.strip():
        return ""

    cleaned = re.sub(r"[^A-Z0-9]", "", raw_value.strip().upper())

    if cleaned.isdigit():
        return f"REC-{cleaned}"

    if cleaned.startswith("REC") and cleaned[3:].isdigit():
        return f"REC-{cleaned[3:]}"

    return raw_value.strip().upper()


class Command(BaseCommand):
    help = "Import locations, System A records and System B entries from CSV files."

    def handle(self, *args, **options):
        data_dir = Path(settings.BASE_DIR) / "data"

        locations_file = data_dir / "locations.csv"
        system_a_file = data_dir / "system_a.csv"
        system_b_file = data_dir / "system_b.csv"

        for file_path in [
            locations_file,
            system_a_file,
            system_b_file,
        ]:
            if not file_path.exists():
                raise CommandError(f"CSV file not found: {file_path}")

        self.stdout.write("Starting CSV import...")

        counts = {
            "locations_read": 0,
            "locations_saved": 0,
            "system_a_read": 0,
            "system_a_saved": 0,
            "system_b_read": 0,
            "system_b_saved": 0,
            "invalid_numbers": 0,
            "invalid_dates": 0,
        }

        with transaction.atomic():

            # 1. Import locations first.
            with open(locations_file, "r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file)

                for row in reader:
                    counts["locations_read"] += 1

                    location_id = row["location_id"].strip()

                    if not location_id:
                        raise CommandError(
                            f"Missing location_id at locations.csv row "
                            f"{counts['locations_read'] + 1}"
                        )

                    Location.objects.update_or_create(
                        location_id=location_id,
                        defaults={
                            "org_id": row["org_id"].strip(),
                            "location_name": row["location_name"].strip(),
                        },
                    )

                    counts["locations_saved"] += 1

            # Cache locations for efficient lookup.
            locations = {
                location.location_id: location
                for location in Location.objects.all()
            }

            # 2. Import System A records.
            with open(system_a_file, "r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file)

                for row in reader:
                    counts["system_a_read"] += 1

                    location_id = row["location_id"].strip()
                    location = locations.get(location_id)

                    if location is None:
                        raise CommandError(
                            f"Unknown location '{location_id}' in "
                            f"system_a.csv row {counts['system_a_read'] + 1}"
                        )

                    base_value = parse_decimal(row["base_value"])
                    adjustment = parse_decimal(row["adjustment"])
                    total_value = parse_decimal(row["total_value"])

                    if row["base_value"].strip() and base_value is None:
                        counts["invalid_numbers"] += 1

                    if row["adjustment"].strip() and adjustment is None:
                        counts["invalid_numbers"] += 1

                    if row["total_value"].strip() and total_value is None:
                        counts["invalid_numbers"] += 1

                    event_date = parse_date(row["event_date"])

                    if row["event_date"].strip() and event_date is None:
                        counts["invalid_dates"] += 1

                    SystemARecord.objects.update_or_create(
                        record_id=row["record_id"].strip(),
                        defaults={
                            "location": location,
                            "event_date": event_date,
                            "event_date_raw": row["event_date"],
                            "category_code": row["category_code"].strip(),
                            "actor_id": row["actor_id"].strip() or None,
                            "base_value": base_value,
                            "base_value_raw": row["base_value"],
                            "adjustment": adjustment,
                            "adjustment_raw": row["adjustment"],
                            "total_value": total_value,
                            "total_value_raw": row["total_value"],
                            "state": row["state"].strip(),
                        },
                    )

                    counts["system_a_saved"] += 1

            # 3. Import System B entries.
            with open(system_b_file, "r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file)

                for row in reader:
                    counts["system_b_read"] += 1

                    location_id = row["location_id"].strip()
                    location = locations.get(location_id)

                    if location is None:
                        raise CommandError(
                            f"Unknown location '{location_id}' in "
                            f"system_b.csv row {counts['system_b_read'] + 1}"
                        )

                    value = parse_decimal(row["value"])

                    if row["value"].strip() and value is None:
                        counts["invalid_numbers"] += 1

                    recorded_on = parse_date(row["recorded_on"])

                    if row["recorded_on"].strip() and recorded_on is None:
                        counts["invalid_dates"] += 1

                    SystemBEntry.objects.update_or_create(
                        entry_id=row["entry_id"].strip(),
                        defaults={
                            "record_ref_raw": row["record_ref"],
                            "record_ref": normalize_ref(row["record_ref"]),
                            "location": location,
                            "recorded_on": recorded_on,
                            "recorded_on_raw": row["recorded_on"],
                            "value": value,
                            "value_raw": row["value"],
                            "label": row["label"],
                        },
                    )

                    counts["system_b_saved"] += 1

        # Transaction completed successfully.
        self.stdout.write(self.style.SUCCESS("\nCSV import completed."))

        for name, count in counts.items():
            self.stdout.write(f"{name}: {count}")

        self.stdout.write(
            self.style.SUCCESS(
                "\nAll CSV rows were processed successfully."
            )
        )
