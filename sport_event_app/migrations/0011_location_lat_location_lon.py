# Generated by Django 4.0 on 2023-06-28 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sport_event_app', '0010_location_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='lat',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='lon',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
