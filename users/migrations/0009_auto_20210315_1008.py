# Generated by Django 3.1.3 on 2021-03-15 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_auto_20210315_1003'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pre_transaction',
            name='qrcode',
        ),
        migrations.RemoveField(
            model_name='transfert',
            name='qrcode',
        ),
        migrations.RemoveField(
            model_name='transfert_direct',
            name='qrcode',
        ),
        migrations.AddField(
            model_name='notification',
            name='qrcode',
            field=models.ImageField(blank=True, default=None, null=True, upload_to=''),
        ),
    ]
