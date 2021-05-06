# Generated by Django 3.1.3 on 2021-05-03 01:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_auto_20210501_2129'),
    ]

    operations = [
        migrations.AddField(
            model_name='transfert_cagnote',
            name='type_transaction',
            field=models.CharField(choices=[(
                'DONATION', 'DONATION'), ('RECOLTE', 'RECOLTE')], default='DONATION', max_length=30),
            preserve_default=False,
        ),
    ]