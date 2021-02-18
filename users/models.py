from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group
from api.models import Agence, Commune
import uuid
from rest_framework import serializers
#from .serializers import TransfertDirectFullSerializer
#from api.serializers import TransactionFullSerializer


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
    CLIENT = 'CLIENT'
    VENDOR = 'VENDOR'

    ROLES = [
        (EMPLOYE_AGENCE, EMPLOYE_AGENCE),
        (RESPONSABLE_AGENCE, RESPONSABLE_AGENCE),
        (AGENT_COMPENSATION, AGENT_COMPENSATION),
        (CLIENT, CLIENT),
        (VENDOR, VENDOR)
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

    class Meta:
        db_table = "model_user"


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
        db_table = "employe"


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


class Client_DigiPay(MyUser, PermissionsMixin):
    tel = models.CharField(max_length=50, blank=True, unique=True)
    email = models.EmailField(null=True, blank=True)
    adresse = models.CharField(max_length=100, null=True, blank=True)
    solde = models.FloatField(default=0.0)
    client = models.IntegerField(null=True)

    @property
    def name(self):
        return self.first_name + " " + self.last_name

    objects = CustomAccountManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role', 'tel']

    def envoyer(self, clientId, montant):
        Client = Client_DigiPay.objects.get(id=clientId)
        if self.solde >= montant:
            self.solde -= montant
            self.save()
            Client.solde += montant
            Client.save()

            transfert = Transfert_Direct(
                expediteur=self,
                destinataire=Client,
                status=TransactionModel.COMFIRMED,
                montant=montant)
            transfert.save()

            transaction = Transaction(
                transaction=transfert, type_transaction=Transaction.ENVOI, date=transfert.date_creation)
            transaction.save()

            result = TransactionFullSerializer(transaction).data
            result['transaction'] = TransfertDirectFullSerializer(
                transfert).data

            # notifications
            msgSelf = Notification(
                user=self, transaction=transfert, status=Notification.ENVOI,
                message="Vous avez effectuer un envoi de " + str(montant) + " MRU vers " + Client.name + ' (' + Client.tel+')')
            msgSelf.save()

            msgClient = Notification(
                user=Client, transaction=transfert, status=Notification.ENVOI,
                message="Vous avez recu un montant de " + str(montant) + " MRU de " + self.name + ' (' + self.tel+')')
            msgClient.save()

            return result
        else:
            return {'msg': "Votre solde est insuffisant pour effectuer cette opération"}

    def envoyer_par_sms(self, tel, montant):
        if self.solde >= montant:
            #self.solde -= montant
            # self.save()
            code_confirmation = str(uuid.uuid4().hex[:8].upper())
            pre_transaction = Pre_Transaction(
                expediteur=self,
                destinataire=tel,
                status=TransactionModel.TO_VALIDATE,
                type_transaction=Pre_Transaction.RETRAIT,
                montant=montant,
                code_secret=code_confirmation)
            pre_transaction.save()

            # notifications
            msgSelf = Notification(
                user=self, transaction=pre_transaction, status=Notification.DEMANDE_RETRAIT,
                message="Vous avez envoyer une demande de retrait de " + str(montant) + " MRU au numero " + str(tel) + ' avec le code confirmation: '+pre_transaction.code_secret)
            msgSelf.save()

            # envoie de sms au numero de tel twiolio

            return {'par_sms': "Opération réussie !"}
        else:
            return {'msg': "Votre solde est insuffisant pour effectuer cette opération"}

    class Meta:
        db_table = "client_digiPay"


class Vendor(MyUser, PermissionsMixin):
    tel = models.CharField(max_length=50, blank=True, unique=True)
    email = models.EmailField(null=True, blank=True)
    adresse = models.CharField(max_length=100, null=True, blank=True)
    solde = models.FloatField(default=0.0)
    client = models.IntegerField(null=True)

    @property
    def name(self):
        return self.first_name

    objects = CustomAccountManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'role', 'tel']

    class Meta:
        db_table = "vendor"


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
    COMFIRMED = 'COMFIRMED'
    STATUS = [
        (NOT_WITHDRAWED, NOT_WITHDRAWED),
        (TO_VALIDATE, TO_VALIDATE),
        (WITHDRAWED, WITHDRAWED),
        (CANCELED, CANCELED),
        (COMFIRMED, COMFIRMED),
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
    #COMP_VERSEMENT = '03'
    #COMP_RETRAIT = '04'
    # TYPES = [
    #   (COMP_VERSEMENT, 'COMP_VERSEMENT'),
    #   (COMP_RETRAIT, 'COMP_RETRAIT'),
    # ]

    agent = models.ForeignKey(
        Agent, related_name="compensations", on_delete=models.CASCADE)
    agence = models.ForeignKey(
        Agence, related_name="compensations", on_delete=models.CASCADE)

    #type_transaction = models.CharField(max_length=4,choices=TYPES,)

    class Meta:
        db_table = "compensation"


class Client(models.Model):
    nom = models.CharField(max_length=100)
    tel = models.CharField(max_length=50, unique=True)
    nni = models.CharField(max_length=50, null=True, blank=True)
    piece = models.ImageField(null=True, blank=True)

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
    code_secret = models.CharField(max_length=200, blank=True, default='')

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
            note=data['note'])
        '''

    # @property
    # def code_secret(self):
    #    return str(uuid.uuid4().hex[:6].upper())
    '''
    def confirmer(self, code):
        if (self.code_secret == code):
            self.status = TransactionModel.COMFIRMED
            self.save()
            return "Paiement confirmé"
        else:
            return "Code incorrect !"
    '''
    class Meta:
        db_table = "transfert"


# Pre-transactions
class Pre_Transaction(TransactionModel):
    PAIEMENT = 'PAIEMENT'
    RETRAIT = 'RETRAIT'
    TYPES = [
        (PAIEMENT, 'PAIEMENT'),
        (RETRAIT, 'RETRAIT'),
    ]
    type_transaction = models.CharField(max_length=30, choices=TYPES,)

    expediteur = models.ForeignKey(
        MyUser, related_name='preTransactions_envoyes', on_delete=models.CASCADE)
    destinataire = models.IntegerField(null=True)
    code_secret = models.CharField(max_length=200, blank=True, default='')

    '''
    def confirmer(self, code):
        if (self.code_secret == code):
            self.status = TransactionModel.COMFIRMED
            self.save()
            return "Pre Transaction confirmé"
        else:
            return "Code incorrect!"
    '''

    def client_retrait(self, agenceId, nom_destinataire):
        expediteur = Client_DigiPay.objects.get(id=self.expediteur.id)
        agence_destination = Agence.objects.get(id=agenceId)
        ###
        if expediteur.solde >= self.montant:
            if agence_destination.solde >= self.montant:
                expediteur.solde -= self.montant
                expediteur.save()
                agence_destination.solde -= self.montant
                agence_destination.retrait += self.montant
                agence_destination.save()
                ##
                categorie = Transfert.SUP_3000 if self.montant > 3000 else Transfert.INF_3000
                temp = list(Client.objects.filter(tel=self.destinataire))
                destinataire = temp[0] if len(temp) > 0 else Client.objects.create(
                    tel=self.destinataire, nom=nom_destinataire)
                transfert = Transfert(agence_destination=agence_destination,
                                      agence_origine=agence_destination, expediteur=expediteur.client,
                                      destinataire=destinataire, montant=self.montant, categorie_transaction=categorie,
                                      status=TransactionModel.WITHDRAWED, code_secret=self.code_secret)
                transfert.save()
                ##
                transaction = Transaction(transaction=transfert, type_transaction=Transaction.RETRAIT,
                                          date=transfert.date_creation, categorie_transaction=transfert.categorie_transaction)
                transaction.save()

                result = TransactionFullSerializer(transaction).data
                result['transaction'] = TransfertFullSerializer(transfert).data

                # notifications
                msgSelf = Notification(
                    user=expediteur, transaction=transfert, status=Notification.RETRAIT,
                    message="Un retrait de " +
                    str(self.montant) +
                    " MRU est enregistrer sur votre compte effectuer par "
                    + destinataire.nom + " (" +
                    str(destinataire.tel) + ") de l'agence "
                    + agence_destination.nom + ' (' + agence_destination.code_agence+')')
                msgSelf.save()

                self.status = TransactionModel.COMFIRMED
                self.save()
                return result
            else:
                return {'msg': "le solde l'agence est insuffisant pour effectuer cette opération"}
        else:
            return {'msg': "le solde du client est insuffisant pour effectuer cette opération"}

    class Meta:
        db_table = "pre_transactions"


class Transfert_Direct(TransactionModel):

    expediteur = models.ForeignKey(
        MyUser, related_name='transferts_direct_envoyes', on_delete=models.CASCADE)
    destinataire = models.ForeignKey(
        MyUser, related_name='transferts_direct_recus', on_delete=models.CASCADE)
    code_secret = models.CharField(max_length=200, blank=True, default='')

    '''
    def confirmer(self, code):
        if (self.code_secret == code):
            self.status = TransactionModel.COMFIRMED
            self.save()
            return "Paiement confirmé"
        else:
            return "Code incorrect !"
    '''
    class Meta:
        db_table = "transfert_direct"


class Notification(models.Model):
    DEMANDE_PAIEMENT = 'DEMANDE_PAIEMENT'
    DEMANDE_RETRAIT = 'DEMANDE_RETRAIT'
    RETRAIT = 'RETRAIT'
    PAIEMENT = 'PAIEMENT'
    ENVOI = 'ENVOI'
    RECHARGE = 'RECHARGE'
    TAGS = ((DEMANDE_PAIEMENT, 'DEMANDE DE PAIEMENT'),
            (DEMANDE_RETRAIT, 'DEMANDE DE RETRAIT'),
            (RETRAIT, 'RETRAIT'),
            (PAIEMENT, 'PAIEMENT'),
            (ENVOI, 'ENVOI'),
            (RECHARGE, 'RECHARGE'))
    user = models.ForeignKey(MyUser, blank=True, on_delete=models.CASCADE)
    transaction = models.ForeignKey(TransactionModel, on_delete=models.CASCADE)

    message = models.CharField(max_length=200, blank=True, default='')
    status = models.CharField(
        max_length=50, choices=TAGS, default="DEMANDE DE PAIEMENT")
    date = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "notification"

# Dashboard models


class Transaction(models.Model):
    TRANSFERT = '01'
    RETRAIT = '02'
    COMP_VERSEMENT = '03'
    COMP_RETRAIT = '04'
    RECHARGE = '05'
    PAIEMENT = '06'
    ENVOI = '07'
    REMBOURSEMENT = '08'
    TYPES = [
        (TRANSFERT, 'TRANSFERT'),
        (RETRAIT, 'RETRAIT'),
        (COMP_VERSEMENT, 'COMP_VERSEMENT'),
        (COMP_RETRAIT, 'COMP_RETRAIT'),
        ###
        (RECHARGE, 'RECHARGE'),
        (PAIEMENT, 'PAIEMENT'),
        (ENVOI, 'ENVOI'),
        (REMBOURSEMENT, 'REMBOURSEMENT'),

    ]

    NONE = 'NONE'
    INF_3000 = 'INF_3000'
    SUP_3000 = 'SUP_3000'
    CATEGORIES = [
        (INF_3000, 'INF_3000'),
        (SUP_3000, 'SUP_3000'),
        (NONE, 'NONE'),
    ]

    # agence = models.ForeignKey(
    #    Agence, related_name='transactions', on_delete=models.CASCADE)
    transaction = models.ForeignKey(
        TransactionModel, on_delete=models.CASCADE)

    type_transaction = models.CharField(
        max_length=50,
        choices=TYPES,
    )
    categorie_transaction = models.CharField(
        max_length=50,
        choices=CATEGORIES,
        default=NONE,
    )
    date = models.DateTimeField()

    @property
    def code_transaction(self):
        # return "TR"+str(self.agence.id).zfill(3)+self.type_transaction+str(self.transaction.id).zfill(5)
        return "TR"+self.type_transaction+str(self.transaction.id).zfill(5)

    class Meta:
        db_table = "transaction"


'''
some duplicates serializers to handle recursive imports
need to improve this part ...
'''


class TransactionFullSerializer(serializers.ModelSerializer):
    #agence = AgenceFullSerializer()
    code_transaction = serializers.CharField()

    class Meta:
        model = Transaction
        fields = '__all__'


class ClientDigiPay_UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    tel = serializers.CharField(required=True)
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = Client_DigiPay
        fields = ('id', 'username', 'first_name', 'last_name',
                  'role', 'password', 'tel', 'email', 'adresse', 'solde', 'client', 'start_date', 'is_active', 'last_login')
        extra_kwargs = {'password': {'write_only': True},
                        'id': {'read_only': True}, 'start_date': {'read_only': True}, 'last_login': {'read_only': True}}


class Vendor_UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    tel = serializers.CharField(required=True)
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = Vendor
        fields = ('id', 'username', 'first_name', 'last_name',
                  'role', 'password', 'tel', 'email', 'adresse', 'solde', 'client', 'start_date', 'is_active', 'last_login')
        extra_kwargs = {'password': {'write_only': True},
                        'id': {'read_only': True}, 'start_date': {'read_only': True}, 'last_login': {'read_only': True}}


class TransfertDirectFullSerializer(serializers.ModelSerializer):
    # Hide not used attributes in exp et dest ...
    # move to models ??
    expediteur = serializers.SerializerMethodField()
    destinataire = serializers.SerializerMethodField()
    code_secret = serializers.CharField()

    class Meta:
        model = Transfert_Direct
        fields = '__all__'

    def get_expediteur(self, instance):
        data = {}
        if instance.expediteur.role == MyUser.CLIENT:
            client = Client_DigiPay.objects.get(id=instance.expediteur.id)
            data = ClientDigiPay_UserSerializer(client).data
            return data
        elif instance.expediteur.role == MyUser.VENDOR:
            vendor = Vendor.objects.get(id=instance.expediteur.id)
            data = Vendor_UserSerializer(vendor).data
            return data
        else:
            return instance.expediteur.id

    def get_destinataire(self, instance):
        data = {}
        if instance.destinataire.role == MyUser.CLIENT:
            client = Client_DigiPay.objects.get(id=instance.destinataire.id)
            data = ClientDigiPay_UserSerializer(client).data
            return data
        elif instance.destinataire.role == MyUser.VENDOR:
            vendor = Vendor.objects.get(id=instance.destinataire.id)
            data = Vendor_UserSerializer(vendor).data
            return data
        else:
            return instance.destinataire.id


class CommuneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commune
        fields = '__all__'


class AgenceFullSerializer(serializers.ModelSerializer):
    commune = CommuneSerializer()

    class Meta:
        model = Agence
        fields = '__all__'


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class TransfertFullSerializer(serializers.ModelSerializer):
    agence_origine = AgenceFullSerializer()
    agence_destination = AgenceFullSerializer()
    destinataire = ClientSerializer()
    expediteur = serializers.SerializerMethodField()
    code_secret = serializers.CharField()

    class Meta:
        model = Transfert
        fields = '__all__'

    def get_expediteur(self, instance):
        data = {}
        if instance.expediteur:
            client = Client.objects.get(id=instance.expediteur)
            data = ClientSerializer(client).data
            return data
        else:
            return None
