from django.db import models


class CostBand(models.Model):
    """Aggregated cost-per-watt band for a system-size/tier/location/installer combination."""

    class InstallerType(models.TextChoices):
        LOCAL = "local", "Local (1–5 crews)"
        REGIONAL = "regional", "Regional (6–20 locations)"
        NATIONAL = "national", "National (21+ locations)"
        UTILITY = "utility", "Utility / Developer"

    system_size_range = models.CharField(max_length=50, db_index=True)  # e.g. "5-8 kW"
    panel_tier = models.CharField(max_length=50, db_index=True)  # standard / premium / premium-plus
    location = models.CharField(max_length=200, db_index=True)  # state or metro label
    installer_type = models.CharField(
        max_length=20, choices=InstallerType.choices, db_index=True
    )

    # Cost per watt percentile bands ($/W)
    p25 = models.DecimalField(max_digits=6, decimal_places=3)
    p50 = models.DecimalField(max_digits=6, decimal_places=3)
    p75 = models.DecimalField(max_digits=6, decimal_places=3)
    p90 = models.DecimalField(max_digits=6, decimal_places=3)

    sample_size = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("system_size_range", "panel_tier", "location", "installer_type")
        indexes = [
            models.Index(
                fields=["system_size_range", "panel_tier"],
                name="costband_size_tier_idx",
            ),
            models.Index(
                fields=["location", "installer_type"],
                name="costband_loc_installer_idx",
            ),
        ]
        ordering = ["location", "system_size_range", "panel_tier"]

    def __str__(self):
        return (
            f"{self.system_size_range} / {self.panel_tier} @ {self.location} "
            f"[{self.installer_type}]"
        )
