# Generated by Django 3.1.3 on 2021-05-18 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0024_auto_20210518_2124'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='solde',
            field=models.FloatField(default=0.0),
        ),
    ]
