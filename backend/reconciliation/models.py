from django.db import models


class Location(models.Model):
    location_id = models.CharField(max_length=50, primary_key=True)
    org_id = models.CharField(max_length=50, db_index=True)
    location_name = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.location_id} - {self.org_id}"


class SystemARecord(models.Model):
    record_id = models.CharField(max_length=50, primary_key=True)

    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="system_a_records"
    )

    event_date = models.DateField(null=True, blank=True)
    event_date_raw = models.CharField(max_length=100, blank=True)

    category_code = models.CharField(max_length=50)
    actor_id = models.CharField(max_length=100, null=True, blank=True)

    base_value = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True
    )
    base_value_raw = models.CharField(max_length=100, blank=True)

    adjustment = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True
    )
    adjustment_raw = models.CharField(max_length=100, blank=True)

    total_value = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True
    )
    total_value_raw = models.CharField(max_length=100, blank=True)

    state = models.CharField(max_length=30)

    def __str__(self):
        return self.record_id


class SystemBEntry(models.Model):
    entry_id = models.CharField(max_length=50, primary_key=True)

    # Keep original reference and its normalized version separately.
    record_ref_raw = models.CharField(max_length=100, blank=True)
    record_ref = models.CharField(max_length=100, blank=True, db_index=True)

    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="system_b_entries"
    )

    recorded_on = models.DateField(null=True, blank=True)
    recorded_on_raw = models.CharField(max_length=100, blank=True)

    value = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True
    )
    value_raw = models.CharField(max_length=100, blank=True)

    label = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.entry_id} - {self.record_ref}"
