# Generated by Django 4.2 on 2023-10-17 16:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("vendors", "0003_alter_vendor_managers_alter_vendor_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vendor",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]