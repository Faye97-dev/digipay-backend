# Generated by Django 3.1.3 on 2021-05-09 16:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0021_auto_20210505_1345'),
    ]

    operations = [
        migrations.AddField(
            model_name='cagnote',
            name='beneficiaire',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='beneficiaire_cagnote', to='users.myuser'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='client_digipay',
            name='date_naissance',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='client_digipay',
            name='identifiant',
            field=models.CharField(max_length=15, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='compensation',
            name='frais_destination',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='compensation',
            name='frais_origine',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='compensation',
            name='frais_societe',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='group_payement',
            name='motif',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='transfert_cagnote',
            name='frais_destination',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='transfert_cagnote',
            name='frais_origine',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='transfert_cagnote',
            name='frais_societe',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='transfert_direct',
            name='frais_destination',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='transfert_direct',
            name='frais_origine',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='transfert_direct',
            name='frais_societe',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='cagnote',
            name='responsable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responsable_cagnote', to=settings.AUTH_USER_MODEL),
        ),
    ]
