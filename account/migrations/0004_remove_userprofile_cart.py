# Generated by Django 4.2 on 2023-09-27 15:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0003_merge_20230927_1545"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userprofile",
            name="cart",
        ),
    ]
