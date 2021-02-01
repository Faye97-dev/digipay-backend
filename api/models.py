from django.db import models
# Create your models here.
HOST = "https://digipaybackend.herokuapp.com/"  # 'http://127.0.0.1:8000/'
#HOST = 'http://192.168.1.28:8000/'
# http://192.168.1.28:3000/


class Commune(models.Model):
    commune_code = models.IntegerField(primary_key=True)
    wilaya = models.CharField(max_length=200)
    commune = models.CharField(max_length=200)
    #wilaya = models.ForeignKey(Wilaya, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.commune) + " : " + str(self.commune_code)

    class Meta:
        db_table = "commune"


class Agence(models.Model):
    AGENCE_INTERN = 'AGENCE_INTERN'
    PARTNER_SILVER = 'PARTNER_SILVER'
    PARTNER_GOLD = 'PARTNER_GOLD'
    TYPES = [
        (AGENCE_INTERN, AGENCE_INTERN),
        (PARTNER_SILVER, PARTNER_SILVER),
        (PARTNER_GOLD, PARTNER_GOLD),
    ]

    nom = models.CharField(max_length=100, unique=True)
    solde = models.FloatField(default=0.0)
    frais = models.FloatField(default=0.0)
    retrait = models.FloatField(default=0.0)
    dette = models.FloatField(default=0.0)
    code_agence = models.CharField(max_length=100, unique=True)
    tel = models.CharField(max_length=100)
    adresse = models.CharField(max_length=100, blank=True, null=True)
    logitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    email = models.EmailField(null=True, blank=True)

    type_agence = models.CharField(
        max_length=25,
        choices=TYPES,
    )
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    online = models.BooleanField(default=False)
    remarque = models.TextField(blank=True, null=True)
    last_date_cloture = models.DateTimeField(null=True)

    class Meta:
        db_table = "agence"
