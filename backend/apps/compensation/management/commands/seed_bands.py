from django.core.management.base import BaseCommand

from apps.compensation.models import CompensationBand


# Realistic salary data indexed by (role, level, location, company_size) → (p25, p50, p75, p90, n)
SEED_DATA = [
    # SF Bay Area — Enterprise
    ("Software Engineer I", "IC3", "San Francisco Bay Area", "enterprise", 145000, 165000, 185000, 210000, 120),
    ("Software Engineer II", "IC4", "San Francisco Bay Area", "enterprise", 175000, 195000, 220000, 255000, 98),
    ("Senior Software Engineer", "IC5", "San Francisco Bay Area", "enterprise", 220000, 250000, 290000, 340000, 85),
    ("Staff Software Engineer", "IC6", "San Francisco Bay Area", "enterprise", 295000, 340000, 400000, 470000, 42),
    ("Product Manager", "IC4", "San Francisco Bay Area", "enterprise", 165000, 185000, 215000, 250000, 60),
    ("Senior Product Manager", "IC5", "San Francisco Bay Area", "enterprise", 205000, 235000, 275000, 320000, 38),
    ("Data Scientist", "IC4", "San Francisco Bay Area", "enterprise", 155000, 180000, 210000, 245000, 55),
    ("Machine Learning Engineer", "IC5", "San Francisco Bay Area", "enterprise", 235000, 270000, 315000, 370000, 30),
    # SF Bay Area — Mid
    ("Software Engineer I", "IC3", "San Francisco Bay Area", "mid", 120000, 140000, 160000, 185000, 80),
    ("Software Engineer II", "IC4", "San Francisco Bay Area", "mid", 145000, 165000, 190000, 220000, 65),
    ("Senior Software Engineer", "IC5", "San Francisco Bay Area", "mid", 185000, 215000, 250000, 295000, 50),
    ("Product Manager", "IC4", "San Francisco Bay Area", "mid", 140000, 160000, 185000, 215000, 40),
    # SF Bay Area — Startup
    ("Software Engineer II", "IC4", "San Francisco Bay Area", "startup", 110000, 130000, 155000, 185000, 45),
    ("Senior Software Engineer", "IC5", "San Francisco Bay Area", "startup", 150000, 175000, 210000, 255000, 35),
    ("Product Manager", "IC4", "San Francisco Bay Area", "startup", 120000, 140000, 165000, 195000, 25),
    # New York Metro — Enterprise
    ("Software Engineer I", "IC3", "New York Metro", "enterprise", 130000, 150000, 170000, 195000, 90),
    ("Software Engineer II", "IC4", "New York Metro", "enterprise", 160000, 180000, 205000, 235000, 75),
    ("Senior Software Engineer", "IC5", "New York Metro", "enterprise", 200000, 230000, 265000, 310000, 60),
    ("Staff Software Engineer", "IC6", "New York Metro", "enterprise", 270000, 310000, 360000, 420000, 28),
    ("Product Manager", "IC4", "New York Metro", "enterprise", 150000, 170000, 195000, 225000, 45),
    ("Data Scientist", "IC4", "New York Metro", "enterprise", 145000, 165000, 190000, 220000, 40),
    # New York Metro — Mid
    ("Software Engineer II", "IC4", "New York Metro", "mid", 135000, 155000, 175000, 200000, 55),
    ("Senior Software Engineer", "IC5", "New York Metro", "mid", 165000, 190000, 220000, 260000, 42),
    # Seattle Metro — Enterprise
    ("Software Engineer I", "IC3", "Seattle Metro", "enterprise", 140000, 158000, 178000, 202000, 85),
    ("Software Engineer II", "IC4", "Seattle Metro", "enterprise", 170000, 190000, 215000, 248000, 70),
    ("Senior Software Engineer", "IC5", "Seattle Metro", "enterprise", 215000, 245000, 280000, 330000, 58),
    ("Staff Software Engineer", "IC6", "Seattle Metro", "enterprise", 280000, 325000, 380000, 445000, 32),
    ("Machine Learning Engineer", "IC5", "Seattle Metro", "enterprise", 225000, 258000, 298000, 348000, 22),
    # Austin Metro — Enterprise
    ("Software Engineer I", "IC3", "Austin Metro", "enterprise", 110000, 125000, 142000, 162000, 65),
    ("Software Engineer II", "IC4", "Austin Metro", "enterprise", 130000, 148000, 168000, 192000, 52),
    ("Senior Software Engineer", "IC5", "Austin Metro", "enterprise", 160000, 185000, 215000, 252000, 40),
    ("Product Manager", "IC4", "Austin Metro", "enterprise", 125000, 142000, 162000, 185000, 30),
    # Austin Metro — Mid
    ("Software Engineer II", "IC4", "Austin Metro", "mid", 105000, 122000, 140000, 162000, 48),
    ("Senior Software Engineer", "IC5", "Austin Metro", "mid", 135000, 155000, 178000, 208000, 35),
    # Austin Metro — Startup
    ("Software Engineer II", "IC4", "Austin Metro", "startup", 90000, 108000, 128000, 150000, 38),
    ("Senior Software Engineer", "IC5", "Austin Metro", "startup", 120000, 140000, 162000, 190000, 28),
    # Remote — Enterprise
    ("Software Engineer II", "IC4", "Remote", "enterprise", 140000, 158000, 178000, 205000, 110),
    ("Senior Software Engineer", "IC5", "Remote", "enterprise", 175000, 200000, 232000, 272000, 88),
    ("Staff Software Engineer", "IC6", "Remote", "enterprise", 240000, 278000, 322000, 378000, 35),
    ("Product Manager", "IC4", "Remote", "enterprise", 130000, 150000, 172000, 198000, 55),
    ("Data Scientist", "IC4", "Remote", "enterprise", 128000, 148000, 170000, 198000, 48),
    # Remote — Mid
    ("Software Engineer II", "IC4", "Remote", "mid", 110000, 128000, 148000, 172000, 85),
    ("Senior Software Engineer", "IC5", "Remote", "mid", 145000, 168000, 195000, 228000, 65),
    # Remote — Startup
    ("Software Engineer II", "IC4", "Remote", "startup", 95000, 112000, 132000, 155000, 60),
    ("Senior Software Engineer", "IC5", "Remote", "startup", 125000, 145000, 170000, 200000, 45),
    # Boston Metro — Enterprise
    ("Software Engineer II", "IC4", "Boston Metro", "enterprise", 150000, 170000, 193000, 222000, 58),
    ("Senior Software Engineer", "IC5", "Boston Metro", "enterprise", 190000, 218000, 252000, 295000, 45),
    ("Data Scientist", "IC4", "Boston Metro", "enterprise", 138000, 158000, 182000, 210000, 35),
    # Denver Metro — Mid
    ("Software Engineer II", "IC4", "Denver Metro", "mid", 112000, 130000, 150000, 175000, 42),
    ("Senior Software Engineer", "IC5", "Denver Metro", "mid", 140000, 162000, 188000, 220000, 32),
]


class Command(BaseCommand):
    help = "Seed the database with realistic compensation band data."

    def handle(self, *args, **options):
        created = 0
        updated = 0

        for role, level, location, company_size, p25, p50, p75, p90, n in SEED_DATA:
            _, was_created = CompensationBand.objects.update_or_create(
                role=role,
                level=level,
                location=location,
                company_size=company_size,
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
