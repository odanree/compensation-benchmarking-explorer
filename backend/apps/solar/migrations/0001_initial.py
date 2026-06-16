from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CostBand",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("system_size_range", models.CharField(db_index=True, max_length=50)),
                ("panel_tier", models.CharField(db_index=True, max_length=50)),
                ("location", models.CharField(db_index=True, max_length=200)),
                ("installer_type", models.CharField(
                    choices=[
                        ("local", "Local (1\u20135 crews)"),
                        ("regional", "Regional (6\u201320 locations)"),
                        ("national", "National (21+ locations)"),
                        ("utility", "Utility / Developer"),
                    ],
                    db_index=True,
                    max_length=20,
                )),
                ("p25", models.DecimalField(decimal_places=3, max_digits=6)),
                ("p50", models.DecimalField(decimal_places=3, max_digits=6)),
                ("p75", models.DecimalField(decimal_places=3, max_digits=6)),
                ("p90", models.DecimalField(decimal_places=3, max_digits=6)),
                ("sample_size", models.PositiveIntegerField(default=0)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["location", "system_size_range", "panel_tier"],
                "unique_together": {("system_size_range", "panel_tier", "location", "installer_type")},
                "indexes": [
                    models.Index(
                        fields=["system_size_range", "panel_tier"],
                        name="costband_size_tier_idx",
                    ),
                    models.Index(
                        fields=["location", "installer_type"],
                        name="costband_loc_installer_idx",
                    ),
                ],
            },
        ),
    ]
