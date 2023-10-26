# Generated by Django 4.2 on 2023-10-26 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="is_online",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="last_active",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
