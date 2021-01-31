from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group
from api.models import Agence


class CustomAccountManager(BaseUserManager):

    def create_superuser(self, username, first_name, last_name, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(username, first_name, last_name, password, **other_fields)

    def create_user(self, username, first_name, last_name, password, **other_fields):
        other_fields.setdefault('is_active', True)
        if not username:
            raise ValueError(_('You must provide an username field'))

        #email = self.normalize_email(email)
        user = self.model(username=username, last_name=last_name,
                          first_name=first_name, **other_fields)
        user.set_password(password)
        user.save()
        return user


class MyUser(AbstractBaseUser, PermissionsMixin):

    #SUPER_ADMIN = 'SUPER_ADMIN'
    #SUPERVISEUR = 'SUPERVISEUR'
    EMPLOYE_AGENCE = 'EMPLOYE_AGENCE'
    RESPONSABLE_AGENCE = 'RESPONSABLE_AGENCE'
    AGENT_COMPENSATION = 'AGENT_COMPENSATION'

    ROLES = [
        (EMPLOYE_AGENCE, EMPLOYE_AGENCE),
        (RESPONSABLE_AGENCE, RESPONSABLE_AGENCE),
        (AGENT_COMPENSATION, AGENT_COMPENSATION)
    ]

    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    start_date = models.DateTimeField(default=timezone.now)
    role = models.CharField(
        max_length=50,
        choices=ROLES,
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    #child_id = models.IntegerField(null=True)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']

    # def set_child_id(self, id):
    #     self.child_id = id
    #     self.save()

    def __str__(self):
        return self.username


class Employee(MyUser, PermissionsMixin):
    tel = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(null=True, blank=True)
    adresse = models.CharField(max_length=100, null=True, blank=True)
    agence = models.ForeignKey(
        Agence, related_name='employes', on_delete=models.CASCADE)

    @property
    def name(self):
        return self.first_name + " " + self.last_name

    objects = CustomAccountManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']

    class Meta:
        db_table = "employee"


class Agent(MyUser, PermissionsMixin):
    tel = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(null=True, blank=True)
    adresse = models.CharField(max_length=100, null=True, blank=True)

    @property
    def name(self):
        return self.first_name + " " + self.last_name

    objects = CustomAccountManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']

    class Meta:
        db_table = "agent"


class Responsable(MyUser, PermissionsMixin):
    tel = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(null=True, blank=True)
    adresse = models.CharField(max_length=100, null=True, blank=True)
    agence = models.OneToOneField(
        Agence, related_name='responsable', on_delete=models.CASCADE)

    @property
    def name(self):
        return self.first_name + " " + self.last_name

    objects = CustomAccountManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']

    class Meta:
        db_table = "responsable"


# Acteurs models

class Cloture(models.Model):
    date = models.DateTimeField(null=True)
    solde = models.FloatField(default=0.0)
    frais = models.FloatField(default=0.0)
    retrait = models.FloatField(default=0.0)
    dette = models.FloatField(default=0.0)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    agence = models.ForeignKey(
        Agence, related_name="clotures", on_delete=models.CASCADE)

    class Meta:
        db_table = "cloture"


class TransactionModel(models.Model):
    NOT_WITHDRAWED = 'NOT_WITHDRAWED'
    TO_VALIDATE = 'TO_VALIDATE'
    WITHDRAWED = 'WITHDRAWED'
    CANCELED = 'CANCELED'
    STATUS = [
        (NOT_WITHDRAWED, NOT_WITHDRAWED),
        (TO_VALIDATE, TO_VALIDATE),
        (WITHDRAWED, WITHDRAWED),
        (CANCELED, CANCELED),
    ]

    montant = models.FloatField(default=0.0)
    motif = models.TextField(blank=True, null=True)
    remarque = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=50,
        choices=STATUS,
    )

    is_edited = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True, null=True)
    date_modifcation = models.DateTimeField(auto_now=True, null=True)
    user_created = models.IntegerField(null=True)
    user_edited = models.IntegerField(null=True)

    class Meta:
        db_table = "transaction_model"


class Compensation(TransactionModel):
    COMP_VERSEMENT = '03'
    COMP_RETRAIT = '04'
    TYPES = [
        (COMP_VERSEMENT, 'COMP_VERSEMENT'),
        (COMP_RETRAIT, 'COMP_RETRAIT'),
    ]

    agent = models.ForeignKey(
        Agent, related_name="compensations", on_delete=models.CASCADE)
    agence = models.ForeignKey(
        Agence, related_name="compensations", on_delete=models.CASCADE)

    type_transaction = models.CharField(
        max_length=4,
        choices=TYPES,
    )

    class Meta:
        db_table = "compensation"


class Client(models.Model):
    nom = models.CharField(max_length=100)
    tel = models.CharField(max_length=50)
    nni = models.CharField(max_length=50, null=True, blank=True)
    piece = models.ImageField(null=True)

    class Meta:
        db_table = "client"


class Transfert(TransactionModel):
    INF_3000 = 'INF_3000'
    SUP_3000 = 'SUP_3000'

    CATEGORIES = [
        (INF_3000, 'INF_3000'),
        (SUP_3000, 'SUP_3000'),
    ]

    agence_origine = models.ForeignKey(
        Agence, related_name='transferts', on_delete=models.CASCADE)
    agence_destination = models.ForeignKey(
        Agence, related_name="retraits", on_delete=models.CASCADE)
    expediteur = models.IntegerField(null=True)
    destinataire = models.ForeignKey(
        Client, related_name='transferts_recus', on_delete=models.CASCADE)

    frais_origine = models.FloatField(default=0.0)
    frais_destination = models.FloatField(default=0.0)
    frais_societe = models.FloatField(default=0.0)

    categorie_transaction = models.CharField(
        max_length=50,
        choices=CATEGORIES,
    )

    def add_transfert(self, *args, **kwargs):
        return super(Transfert, self).save(*args, **kwargs)
        '''item = Transfert(agence_origine=data['agence_origine'],
                         agence_destination=data['agence_destination'],
                         destinataire=data['destinataire'],
                         categorie_transaction=data['categorie_transaction'],
                         status=data['status'],
                         solde=data['solde'],
                         frais_origine=data['frais_origine'],
                         frais_destination=data['frais_destination'],
                         remarque=data['remarque'],
                         note=data['note'])'''

    @property
    def code_secret(self):
        return 'random'

    class Meta:
        db_table = "transfert"


# Dashboard models

class Transaction(models.Model):
    TRANSFERT = '01'
    RETRAIT = '02'
    COMP_VERSEMENT = '03'
    COMP_RETRAIT = '04'
    TYPES = [
        (TRANSFERT, 'TRANSFERT'),
        (RETRAIT, 'RETRAIT'),
        (COMP_VERSEMENT, 'COMP_VERSEMENT'),
        (COMP_RETRAIT, 'COMP_RETRAIT'),
    ]

    NONE = 'NONE'
    INF_3000 = 'INF_3000'
    SUP_3000 = 'SUP_3000'
    CATEGORIES = [
        (INF_3000, 'INF_3000'),
        (SUP_3000, 'SUP_3000'),
        (NONE, 'NONE'),
    ]

    agence = models.ForeignKey(
        Agence, related_name='transactions', on_delete=models.CASCADE)
    transaction = models.ForeignKey(
        TransactionModel, on_delete=models.CASCADE)

    type_transaction = models.CharField(
        max_length=50,
        choices=TYPES,
    )
    categorie_transaction = models.CharField(
        max_length=50,
        choices=CATEGORIES,
    )
    date = models.DateTimeField()

    @property
    def code_transaction(self):
        return "TR"+str(self.agence.id).zfill(3)+self.type_transaction+str(self.transaction.id).zfill(5)
