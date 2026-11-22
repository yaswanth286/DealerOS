
from decimal import Decimal

from django.test import TestCase

from reconciliation.models import Location, SystemARecord, SystemBEntry
from reconciliation.services import reconcile_organization


class ReconciliationTests(TestCase):
    def setUp(self):
        self.location_a = Location.objects.create(
            location_id="LOC-A",
            org_id="ORG-A",
            location_name="Location A",
        )

        self.location_b = Location.objects.create(
            location_id="LOC-B",
            org_id="ORG-B",
            location_name="Location B",
        )

    def create_a_record(self, record_id, value, location=None):
        return SystemARecord.objects.create(
            record_id=record_id,
            location=location or self.location_a,
            category_code="TEST",
            total_value=Decimal(value) if value is not None else None,
            state="ACTIVE",
        )

    def create_b_entry(self, entry_id, record_ref, value, label="", location=None):
        return SystemBEntry.objects.create(
            entry_id=entry_id,
            record_ref_raw=record_ref,
            record_ref=record_ref,
            location=location or self.location_a,
            value=Decimal(value) if value is not None else None,
            label=label,
        )

    def test_record_missing_in_system_b(self):
        self.create_a_record("REC-1001", "500.00")

        results = reconcile_organization("ORG-A")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["reason"], "MISSING_IN_B")
        self.assertEqual(results[0]["record_id"], "REC-1001")

    def test_orphan_entry_in_system_b(self):
        self.create_b_entry("ENTRY-1", "REC-9999", "250.00")

        results = reconcile_organization("ORG-A")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["reason"], "ORPHAN_IN_B")
        self.assertEqual(results[0]["record_id"], "REC-9999")

    def test_duplicate_entries_in_system_b(self):
        self.create_a_record("REC-1002", "500.00")

        self.create_b_entry("ENTRY-2", "REC-1002", "250.00")
        self.create_b_entry("ENTRY-3", "REC-1002", "250.00")

        results = reconcile_organization("ORG-A")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["reason"], "DUPLICATE_IN_B")

    def test_value_mismatch_between_systems(self):
        self.create_a_record("REC-1003", "500.00")
        self.create_b_entry("ENTRY-4", "REC-1003", "450.00")

        results = reconcile_organization("ORG-A")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["reason"], "VALUE_MISMATCH")
        self.assertEqual(results[0]["a_value"], Decimal("500.00"))
        self.assertEqual(results[0]["b_value"], Decimal("450.00"))
        self.assertEqual(results[0]["difference"], Decimal("50.00"))

    def test_valid_split_entries_are_not_duplicates(self):
        self.create_a_record("REC-1004", "100.00")

        self.create_b_entry(
            "ENTRY-5", "REC-1004", "40.00", "Part 1 of 2"
        )
        self.create_b_entry(
            "ENTRY-6", "REC-1004", "60.00", "Part 2 of 2"
        )

        results = reconcile_organization("ORG-A")

        self.assertEqual(results, [])

    def test_records_from_another_organization_are_not_used(self):
        self.create_a_record("REC-1005", "500.00", self.location_a)

        self.create_b_entry(
            "ENTRY-7",
            "REC-1005",
            "500.00",
            location=self.location_b,
        )

        results = reconcile_organization("ORG-A")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["reason"], "MISSING_IN_B")
        self.assertEqual(results[0]["record_id"], "REC-1005")
        self.assertEqual(results[0]["location"], "LOC-A")
