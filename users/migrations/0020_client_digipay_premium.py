# Generated by Django 3.1.3 on 2021-05-05 02:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0019_auto_20210505_0206'),
    ]

    operations = [
        migrations.AddField(
            model_name='client_digipay',
            name='premium',
            field=models.BooleanField(default=False),
        ),
    ]