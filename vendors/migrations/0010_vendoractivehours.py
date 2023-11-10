# Generated by Django 4.2 on 2023-11-10 17:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("vendors", "0009_vendor_date_of_birth_vendor_email_vendor_full_name_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="VendorActiveHours",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "day_of_week",
                    models.IntegerField(
                        choices=[
                            (0, "Sunday"),
                            (1, "Monday"),
                            (2, "Tuesday"),
                            (3, "Wednesday"),
                            (4, "Thursday"),
                            (5, "Friday"),
                            (6, "Saturday"),
                        ]
                    ),
                ),
                ("start_time", models.TimeField()),
                ("end_time", models.TimeField()),
                ("is_active", models.BooleanField(default=True)),
                (
                    "vendor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="vendors.vendor"
                    ),
                ),
            ],
            options={
                "unique_together": {
                    ("vendor", "day_of_week", "start_time", "end_time")
                },
            },
        ),
    ]
