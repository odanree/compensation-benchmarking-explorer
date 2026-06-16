from django.core.management.base import BaseCommand

from apps.compensation.models import CostBand


# Solar installation cost-per-watt benchmarks ($/W)
# Indexed by (system_size_range, panel_tier, location, installer_type) → (p25, p50, p75, p90, n)
SEED_DATA = [
    # --- California ---
    ("3-5 kW",  "standard",     "California", "local",    3.10, 3.50, 3.90, 4.40, 85),
    ("3-5 kW",  "premium",      "California", "local",    3.40, 3.85, 4.30, 4.85, 62),
    ("3-5 kW",  "premium-plus", "California", "local",    3.80, 4.30, 4.80, 5.40, 28),
    ("5-8 kW",  "standard",     "California", "local",    2.95, 3.35, 3.75, 4.20, 120),
    ("5-8 kW",  "premium",      "California", "local",    3.25, 3.70, 4.15, 4.65, 95),
    ("5-8 kW",  "premium-plus", "California", "local",    3.60, 4.10, 4.60, 5.15, 42),
    ("5-8 kW",  "standard",     "California", "national", 2.80, 3.20, 3.60, 4.05, 200),
    ("5-8 kW",  "premium",      "California", "national", 3.10, 3.55, 4.00, 4.50, 155),
    ("8-12 kW", "standard",     "California", "local",    2.75, 3.15, 3.55, 4.00, 88),
    ("8-12 kW", "premium",      "California", "local",    3.05, 3.50, 3.95, 4.45, 70),
    ("8-12 kW", "standard",     "California", "national", 2.65, 3.05, 3.45, 3.90, 175),
    ("8-12 kW", "premium",      "California", "national", 2.95, 3.40, 3.85, 4.35, 130),
    ("12 kW+",  "standard",     "California", "national", 2.50, 2.90, 3.30, 3.75, 65),
    ("12 kW+",  "premium",      "California", "national", 2.80, 3.25, 3.70, 4.20, 48),

    # --- Texas ---
    ("3-5 kW",  "standard",     "Texas", "local",    2.70, 3.05, 3.45, 3.90, 70),
    ("3-5 kW",  "premium",      "Texas", "local",    3.00, 3.40, 3.85, 4.35, 48),
    ("5-8 kW",  "standard",     "Texas", "local",    2.55, 2.90, 3.30, 3.75, 105),
    ("5-8 kW",  "premium",      "Texas", "local",    2.85, 3.25, 3.70, 4.20, 78),
    ("5-8 kW",  "standard",     "Texas", "national", 2.40, 2.75, 3.15, 3.60, 180),
    ("5-8 kW",  "premium",      "Texas", "national", 2.70, 3.10, 3.55, 4.05, 135),
    ("8-12 kW", "standard",     "Texas", "national", 2.25, 2.60, 3.00, 3.45, 145),
    ("8-12 kW", "premium",      "Texas", "national", 2.55, 2.95, 3.40, 3.90, 110),
    ("12 kW+",  "standard",     "Texas", "national", 2.10, 2.45, 2.85, 3.30, 55),

    # --- Florida ---
    ("3-5 kW",  "standard",     "Florida", "local",    2.80, 3.15, 3.55, 4.00, 65),
    ("5-8 kW",  "standard",     "Florida", "local",    2.65, 3.00, 3.40, 3.85, 98),
    ("5-8 kW",  "premium",      "Florida", "local",    2.95, 3.35, 3.80, 4.30, 72),
    ("5-8 kW",  "standard",     "Florida", "national", 2.50, 2.85, 3.25, 3.70, 165),
    ("8-12 kW", "standard",     "Florida", "national", 2.35, 2.70, 3.10, 3.55, 130),
    ("8-12 kW", "premium",      "Florida", "national", 2.65, 3.05, 3.50, 4.00, 100),

    # --- Arizona ---
    ("3-5 kW",  "standard",     "Arizona", "local",    2.75, 3.10, 3.50, 3.95, 58),
    ("5-8 kW",  "standard",     "Arizona", "local",    2.60, 2.95, 3.35, 3.80, 88),
    ("5-8 kW",  "premium",      "Arizona", "local",    2.90, 3.30, 3.75, 4.25, 65),
    ("5-8 kW",  "standard",     "Arizona", "national", 2.45, 2.80, 3.20, 3.65, 150),
    ("8-12 kW", "standard",     "Arizona", "national", 2.30, 2.65, 3.05, 3.50, 118),

    # --- New York ---
    ("5-8 kW",  "standard",     "New York", "local",    3.20, 3.60, 4.05, 4.55, 75),
    ("5-8 kW",  "premium",      "New York", "local",    3.50, 3.95, 4.45, 5.00, 55),
    ("5-8 kW",  "standard",     "New York", "national", 3.05, 3.45, 3.90, 4.40, 130),
    ("8-12 kW", "standard",     "New York", "national", 2.90, 3.30, 3.75, 4.25, 98),
    ("8-12 kW", "premium",      "New York", "national", 3.20, 3.65, 4.15, 4.70, 72),

    # --- Massachusetts ---
    ("5-8 kW",  "standard",     "Massachusetts", "local",    3.30, 3.75, 4.20, 4.75, 52),
    ("5-8 kW",  "premium",      "Massachusetts", "local",    3.65, 4.15, 4.65, 5.25, 38),
    ("5-8 kW",  "standard",     "Massachusetts", "national", 3.15, 3.60, 4.05, 4.55, 95),
    ("8-12 kW", "standard",     "Massachusetts", "national", 3.00, 3.45, 3.90, 4.40, 75),

    # --- Washington ---
    ("5-8 kW",  "standard",     "Washington", "local",    2.80, 3.20, 3.60, 4.10, 60),
    ("5-8 kW",  "premium",      "Washington", "local",    3.10, 3.55, 4.00, 4.55, 42),
    ("8-12 kW", "standard",     "Washington", "national", 2.65, 3.05, 3.50, 4.00, 88),

    # --- Colorado ---
    ("5-8 kW",  "standard",     "Colorado", "local",    2.90, 3.30, 3.70, 4.20, 55),
    ("5-8 kW",  "standard",     "Colorado", "national", 2.75, 3.15, 3.60, 4.10, 95),
    ("8-12 kW", "standard",     "Colorado", "national", 2.60, 3.00, 3.45, 3.95, 72),
]


class Command(BaseCommand):
    help = "Seed the database with solar installation cost-per-watt benchmark data."

    def handle(self, *args, **options):
        created = 0
        updated = 0

        for system_size_range, panel_tier, location, installer_type, p25, p50, p75, p90, n in SEED_DATA:
            _, was_created = CostBand.objects.update_or_create(
                system_size_range=system_size_range,
                panel_tier=panel_tier,
                location=location,
                installer_type=installer_type,
                defaults={
                    "p25": p25,
                    "p50": p50,
                    "p75": p75,
                    "p90": p90,
                    "sample_size": n,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created: {created}, Updated: {updated}, Total: {created + updated}"
            )
        )
