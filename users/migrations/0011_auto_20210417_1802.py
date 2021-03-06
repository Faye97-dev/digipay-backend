# Generated by Django 3.1.3 on 2021-04-17 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_auto_20210415_0955'),
    ]

    operations = [
        migrations.AddField(
            model_name='client_digipay',
            name='on_hold',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='pre_transaction',
            name='delai',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='transfert_direct',
            name='libele',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AddField(
            model_name='vendor',
            name='on_hold',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='role',
            field=models.CharField(choices=[('SYSADMIN', 'SYSADMIN'), ('EMPLOYE_AGENCE', 'EMPLOYE_AGENCE'), ('RESPONSABLE_AGENCE', 'RESPONSABLE_AGENCE'), ('AGENT_COMPENSATION', 'AGENT_COMPENSATION'), ('CLIENT', 'CLIENT'), ('VENDOR', 'VENDOR')], max_length=50),
        ),
    ]
