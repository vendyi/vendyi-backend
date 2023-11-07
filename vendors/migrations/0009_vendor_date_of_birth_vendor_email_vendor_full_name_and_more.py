# Generated by Django 4.2 on 2023-11-07 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vendors", "0008_wallet_transaction"),
    ]

    operations = [
        migrations.AddField(
            model_name="vendor",
            name="date_of_birth",
            field=models.DateField(),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="vendor",
            name="email",
            field=models.EmailField(max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="vendor",
            name="full_name",
            field=models.CharField(max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="vendor",
            name="momo_number",
            field=models.CharField(max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="vendor",
            name="momo_type",
            field=models.IntegerField(
                choices=[(0, "MTN"), (1, "Vodafone"), (2, "Airtel-Tigo"), (3, "Other")],
                default=1,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="vendor",
            name="pin",
            field=models.CharField(max_length=5),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="vendor",
            name="product_or_service",
            field=models.CharField(max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="vendor",
            name="security_answer",
            field=models.CharField(max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="vendor",
            name="security_question",
            field=models.CharField(max_length=255),
            preserve_default=False,
        ),
    ]
