# Generated by Django 4.2.4 on 2023-08-22 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ProduceTrack', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_admin',
            field=models.BooleanField(default=False),
        ),
    ]
