# Generated by Django 4.0 on 2023-06-28 08:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sport_event_app', '0011_location_lat_location_lon'),
    ]

    operations = [
        migrations.RenameField(
            model_name='location',
            old_name='location_address',
            new_name='address',
        ),
    ]
