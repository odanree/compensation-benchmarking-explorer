from django.db import models


class CompensationBand(models.Model):
    """Aggregated compensation band for a role/level/location/company-size combination."""

    class CompanySize(models.TextChoices):
        STARTUP = "startup", "Startup (1-50)"
        SMALL = "small", "Small (51-200)"
        MID = "mid", "Mid (201-1,000)"
        LARGE = "large", "Large (1,001-5,000)"
        ENTERPRISE = "enterprise", "Enterprise (5,000+)"

    role = models.CharField(max_length=200, db_index=True)
    level = models.CharField(max_length=50, db_index=True)
    location = models.CharField(max_length=200, db_index=True)
    company_size = models.CharField(
        max_length=20, choices=CompanySize.choices, db_index=True
    )

    # Annual total compensation percentile bands (USD)
    p25 = models.DecimalField(max_digits=10, decimal_places=2)
    p50 = models.DecimalField(max_digits=10, decimal_places=2)
    p75 = models.DecimalField(max_digits=10, decimal_places=2)
    p90 = models.DecimalField(max_digits=10, decimal_places=2)

    sample_size = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("role", "level", "location", "company_size")
        indexes = [
            models.Index(fields=["role", "level"]),
            models.Index(fields=["location", "company_size"]),
        ]
        ordering = ["role", "level"]

    def __str__(self):
        return f"{self.role} ({self.level}) @ {self.location} [{self.company_size}]"
