
import re
from collections import defaultdict
from decimal import Decimal

from reconciliation.models import SystemARecord, SystemBEntry


def normalize_reference(value):
    cleaned = re.sub(r"[^A-Z0-9]", "", (value or "").upper())

    if cleaned.isdigit():
        return f"REC-{cleaned}"

    if cleaned.startswith("REC") and cleaned[3:].isdigit():
        return f"REC-{cleaned[3:]}"

    return (value or "").strip().upper()


def is_valid_split(entries):
    if len(entries) < 2:
        return False

    parts = []

    for entry in entries:
        match = re.search(
            r"part\s+(\d+)\s+of\s+(\d+)",
            entry.label or "",
            re.IGNORECASE,
        )

        if not match:
            return False

        parts.append((int(match.group(1)), int(match.group(2))))

    total = len(entries)

    return (
        all(part_total == total for _, part_total in parts)
        and sorted(number for number, _ in parts) == list(range(1, total + 1))
    )


def reconcile_organization(org_id):
    a_records = (
        SystemARecord.objects
        .select_related("location")
        .filter(location__org_id=org_id)
    )

    b_entries = (
        SystemBEntry.objects
        .select_related("location")
        .filter(location__org_id=org_id)
    )

    a_by_ref = {}
    voided = set()

    for record in a_records:
        ref = normalize_reference(record.record_id)

        if record.state.upper() == "VOIDED":
            voided.add(ref)
        else:
            a_by_ref[ref] = record

    b_by_ref = defaultdict(list)

    for entry in b_entries:
        ref = normalize_reference(entry.record_ref)
        if ref:
            b_by_ref[ref].append(entry)

    results = []

    def add_result(reason, record_id, location, a_value, b_value):
        difference = None
        if a_value is not None and b_value is not None:
            difference = a_value - b_value

        results.append({
            "reason": reason,
            "record_id": record_id,
            "location": location,
            "a_value": a_value,
            "b_value": b_value,
            "difference": difference,
        })

    # Check every active System A record.
    for ref, record in a_by_ref.items():
        entries = b_by_ref.get(ref, [])

        if not entries:
            add_result(
                "MISSING_IN_B", record.record_id,
                record.location.location_id, record.total_value, None
            )
            continue

        b_total = None
        if all(entry.value is not None for entry in entries):
            b_total = sum(
                (entry.value for entry in entries),
                Decimal("0.00"),
            )

        if len(entries) > 1:
            if not is_valid_split(entries):
                add_result(
                    "DUPLICATE_IN_B", record.record_id,
                    record.location.location_id, record.total_value, b_total
                )
                continue

        if (
            record.total_value is None
            or b_total is None
            or record.total_value != b_total
        ):
            add_result(
                "VALUE_MISMATCH", record.record_id,
                record.location.location_id, record.total_value, b_total
            )

    # Check B entries without a matching active A record.
    for ref, entries in b_by_ref.items():
        if ref in a_by_ref or ref in voided:
            continue

        b_total = None
        if all(entry.value is not None for entry in entries):
            b_total = sum(
                (entry.value for entry in entries),
                Decimal("0.00"),
            )

        add_result(
            "ORPHAN_IN_B",
            ref,
            entries[0].location.location_id,
            None,
            b_total,
        )

    return sorted(results, key=lambda x: (x["reason"], x["record_id"]))
