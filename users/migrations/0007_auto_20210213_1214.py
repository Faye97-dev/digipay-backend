# Generated by Django 3.1.3 on 2021-02-13 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20210213_1154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='piece',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
