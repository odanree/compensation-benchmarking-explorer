from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CompensationBand",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(db_index=True, max_length=200)),
                ("level", models.CharField(db_index=True, max_length=50)),
                ("location", models.CharField(db_index=True, max_length=200)),
                ("company_size", models.CharField(
                    choices=[
                        ("startup", "Startup (1-50)"),
                        ("small", "Small (51-200)"),
                        ("mid", "Mid (201-1,000)"),
                        ("large", "Large (1,001-5,000)"),
                        ("enterprise", "Enterprise (5,000+)"),
                    ],
                    db_index=True,
                    max_length=20,
                )),
                ("p25", models.DecimalField(decimal_places=2, max_digits=10)),
                ("p50", models.DecimalField(decimal_places=2, max_digits=10)),
                ("p75", models.DecimalField(decimal_places=2, max_digits=10)),
                ("p90", models.DecimalField(decimal_places=2, max_digits=10)),
                ("sample_size", models.PositiveIntegerField(default=0)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["role", "level"],
                "unique_together": {("role", "level", "location", "company_size")},
                "indexes": [
                    models.Index(fields=["role", "level"], name="comp_band_role_level_idx"),
                    models.Index(fields=["location", "company_size"], name="comp_band_loc_size_idx"),
                ],
            },
        ),
    ]
