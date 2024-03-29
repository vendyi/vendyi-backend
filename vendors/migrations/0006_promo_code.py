# Generated by Django 4.2 on 2023-10-23 15:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("vendors", "0005_alter_vendor_user"),
    ]

    operations = [
        migrations.CreateModel(
            name="Promo_Code",
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
                ("code", models.CharField(max_length=255, unique=True)),
                (
                    "discount_percentage",
                    models.DecimalField(decimal_places=2, max_digits=5),
                ),
                ("discount_start_date", models.DateField(blank=True, null=True)),
                ("discount_end_date", models.DateField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                (
                    "vendor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="vendors.vendor"
                    ),
                ),
            ],
        ),
    ]
