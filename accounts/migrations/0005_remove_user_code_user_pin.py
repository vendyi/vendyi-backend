# Generated by Django 4.2 on 2023-11-11 15:01

from django.db import migrations, models
import django_cryptography.fields


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_alter_user_is_active"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="code",
        ),
        migrations.AddField(
            model_name="user",
            name="pin",
            field=django_cryptography.fields.encrypt(
                models.CharField(blank=True, max_length=5, null=True)
            ),
        ),
    ]
