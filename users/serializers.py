from django.forms.models import model_to_dict
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers, exceptions
from users.models import MyUser, Agent, Employee, Responsable, Compensation, ClientDigiPay, Client, Vendor, Facturier, TransfertDirect, PreTransaction, SysAdmin
from users.models import Cagnote, ParticipantsCagnote, TransfertCagnote, GroupPayement, BeneficiaresGrpPayement, ServicesInterFacturier
from api.models import Agence
from api.serializers import AgenceSerializer, AgenceFullSerializer
from .service import random_with_N_digits
import json
# register users


class Agent_UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(min_length=4, write_only=True)

    class Meta:
        model = Agent
        fields = ('id', 'username', 'first_name', 'last_name',
                  'role', 'password', 'tel', 'email', 'adresse', 'solde', 'start_date', 'is_active', 'last_login',
                  'date_naissance', 'identifiant', 'compte_banquaire')
        extra_kwargs = {'password': {'write_only': True},
                        'id': {'read_only': True}, 'start_date': {'read_only': True}, 'last_login': {'read_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)

        instance.save()
        # instance.set_child_id(instance.id)

        return instance


class Agent_ProfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ('id', 'username', 'first_name', 'role',
                  'last_name', 'tel', 'email', 'adresse')


class SysAdmin_UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(min_length=4, write_only=True)

    class Meta:
        model = SysAdmin
        fields = ('id', 'username', 'first_name', 'last_name',
                  'role', 'password', 'tel', 'email', 'adresse', 'start_date', 'is_active', 'last_login',
                  'date_naissance', 'identifiant', 'compte_banquaire')
        extra_kwargs = {'password': {'write_only': True},
                        'id': {'read_only': True}, 'start_date': {'read_only': True}, 'last_login': {'read_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)

        instance.save()
        # instance.set_child_id(instance.id)

        return instance


class Employe_UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(min_length=4, write_only=True)

    class Meta:
        model = Employee
        fields = ('id', 'username', 'first_name', 'last_name',
                  'role', 'password', 'tel', 'email', 'adresse', 'agence', 'start_date', 'is_active', 'last_login')
        extra_kwargs = {'password': {'write_only': True},
                        'id': {'read_only': True}, 'start_date': {'read_only': True}, 'last_login': {'read_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)

        if password is not None:
            instance.set_password(password)

        instance.save()

        return instance


class EmployeFullSerializer(serializers.ModelSerializer):
    agence = AgenceSerializer()

    class Meta:
        model = Employee
        fields = ('id', 'username', 'first_name', 'last_name',
                  'role', 'password', 'tel', 'email', 'adresse', 'agence', 'start_date', 'is_active', 'last_login',
                  'date_naissance', 'identifiant', 'compte_banquaire')
        extra_kwargs = {'password': {'write_only': True},
                        'id': {'read_only': True}, 'start_date': {'read_only': True}, 'last_login': {'read_only': True}}


class Employe_ProfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('id', 'username', 'first_name', 'role',
                  'last_name', 'tel', 'email', 'adresse')


class Responsable_UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(min_length=4, write_only=True)
    agence = AgenceSerializer()

    class Meta:
        model = Responsable
        fields = ('id', 'username', 'first_name', 'last_name',
                  'role', 'password', 'tel', 'email', 'adresse', 'agence', 'start_date', 'is_active', 'last_login',
                  'date_naissance', 'identifiant', 'compte_banquaire')
        extra_kwargs = {'password': {'write_only': True},
                        'id': {'read_only': True}, 'start_date': {'read_only': True}, 'last_login': {'read_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        agence = validated_data.pop('agence')
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)

        instance.agence = Agence.objects.create(**agence)

        instance.save()

        return instance


class Responsable_ProfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Responsable
        fields = ('id', 'username', 'first_name', 'role',
                  'last_name', 'tel', 'email', 'adresse')


class ClientDigiPay_UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    tel = serializers.CharField(required=True)
    password = serializers.CharField(min_length=4, write_only=True)

    class Meta:
        model = ClientDigiPay
        fields = ('id', 'device_connecte', 'premium', 'username', 'first_name', 'last_name',
                  'role', 'password', 'tel', 'email', 'adresse', 'solde', "on_hold", 'client', 'start_date', 'is_active', 'last_login',
                  'date_naissance', 'identifiant', 'compte_banquaire')
        extra_kwargs = {'password': {'write_only': True}, 'device_connecte': {'write_only': True},
                        'id': {'read_only': True}, 'start_date': {'read_only': True}, 'last_login': {'read_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)

        if password is not None:
            instance.set_password(password)
        instance.save()
        ##
        client = Client(nom=instance.first_name + ' ' +
                        instance.last_name, tel=instance.tel)
        client.save()
        ##
        instance.client = client.id
        instance.save()
        return instance


class CLientDigipay_ProfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientDigiPay
        fields = ('id', 'username', 'first_name', 'role',
                  'last_name', 'tel', 'email', 'adresse')


class Vendor_UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    tel = serializers.CharField(required=True)
    password = serializers.CharField(min_length=4, write_only=True)

    class Meta:
        model = Vendor
        fields = ('id', "myId", 'username', 'first_name', 'last_name',
                  'role', 'password', 'tel', 'email', 'adresse', 'solde', "on_hold", 'client', 'start_date', 'is_active', 'last_login',
                  'date_naissance', 'identifiant', 'compte_banquaire')
        extra_kwargs = {'password': {'write_only': True},
                        'id': {'read_only': True}, 'start_date': {'read_only': True}, 'last_login': {'read_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)

        if password is not None:
            instance.set_password(password)

        ##
        vendors_Id = [item.myId for item in Vendor.objects.all()]
        repeat = True
        while repeat:
            self_vendorId = "0"+str(random_with_N_digits(4))
            repeat = self_vendorId in vendors_Id
            print(self_vendorId, repeat)

        instance.myId = self_vendorId
        instance.save()

        ##
        client = Client(nom=instance.first_name, tel=instance.tel)
        client.save()
        ##
        instance.client = client.id
        instance.save()

        return instance


class Vendor_ProfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ('id', 'username', 'first_name', 'role',
                  'last_name', 'tel', 'email', 'adresse', 'myId')


class Facturier_UserSerializer(serializers.ModelSerializer):
    #tel = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    password = serializers.CharField(min_length=4, write_only=True)

    class Meta:
        model = Facturier
        fields = ('id', 'username', 'first_name', 'last_name',
                  'role', 'password', 'email', 'adresse', 'solde', 'start_date', 'is_active', 'last_login',
                  'date_naissance', 'identifiant', 'compte_banquaire')
        extra_kwargs = {'password': {'write_only': True},
                        'id': {'read_only': True}, 'start_date': {'read_only': True}, 'last_login': {'read_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)

        # generate random username
        if password is not None:
            instance.set_password(password)
        instance.save()

        return instance


class Facturier_ProfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facturier
        fields = ('id', 'username', 'first_name', 'role', 'date_naissance',
                  'identifiant', 'compte_banquaire', 'email', 'adresse')


'''
class DigipayServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigiPayServices
        fields = '__all__'
'''


class ServicesInterFacturierSerializer(serializers.ModelSerializer):
    #service = DigipayServicesSerializer()

    class Meta:
        model = ServicesInterFacturier
        fields = ('id', 'service')


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    # login
    #name = serializers.CharField(required=False)

    def validate(self, attrs):
        #request_data = json.loads(request.body.decode('utf-8'))
        #login_success = False

        device_authorized = False
        is_authenticated = False
        data = None
        try:
            request = self.context['request']
            request_data = request.data
        except:
            device_authorized = True
            print("Request error")
            raise exceptions.AuthenticationFailed("Request error !", "error")
        else:
            try:
                user = MyUser.objects.get(username=request_data['username'])
            except:
                device_authorized = True
                print("Utilisateur Inexistant !")
                raise exceptions.AuthenticationFailed(
                    "Utilisateur Inexistant !", "error")
            else:
                if user.role == MyUser.CLIENT:
                    if 'debugMode' in request_data.keys():
                        if request_data['debugMode']:
                            device_authorized = True
                            print("Web connexion mode !")
                    else:
                        user = ClientDigiPay.objects.get(id=user.id)
                        if 'device_connecte' in request_data.keys():
                            if user.device_connecte:
                                if user.device_connecte == request_data['device_connecte']:
                                    print("Device_connecte success !")
                                    # check credentials of user
                                    device_authorized = True
                                    data = super().validate(attrs)
                                    # if login success
                                    is_authenticated = True
                                else:
                                    device_authorized = False
                                    print("Device_connecte invalid !")
                            else:
                                # check credentials of user
                                device_authorized = True
                                data = super().validate(attrs)
                                # if login success
                                is_authenticated = True

                                user.device_connecte = request_data['device_connecte']
                                user.save()
                                print("First time login !")
                        else:
                            device_authorized = False
                            print("Device connecte non renseigner !")
                else:
                    device_authorized = True
                    print("Not a client user !")
        finally:
            if not device_authorized:
                error_msg = "Téléphone non autorisé !"
                error_name = "device_connecte"
                raise exceptions.AuthenticationFailed(
                    error_msg, error_name)
            else:
                if not is_authenticated:
                    data = super().validate(attrs)

                refresh = self.get_token(self.user)
                data['refresh'] = str(refresh)
                data['access'] = str(refresh.access_token)

                # extra responses here
                if self.user.role == MyUser.RESPONSABLE_AGENCE:
                    responsable = Responsable.objects.get(id=self.user.id)
                    agence = Agence.objects.get(responsable__id=self.user.id)
                    data['agence'] = model_to_dict(agence)
                    data['agence']['last_date_cloture'] = data['agence']['last_date_cloture'].strftime(
                        "%d-%m-%Y %H:%M:%S") if data['agence']['last_date_cloture'] else data['agence']['last_date_cloture']
                    # print(data['agence']['last_date_cloture'])
                    data.update(model_to_dict(responsable, fields=['id', 'username', 'first_name', 'last_name',
                                                                   'role', 'tel', 'email', 'adresse', 'start_date', 'is_active', 'last_login',
                                                                   'date_naissance', 'identifiant', 'compte_banquaire']))
                    data['last_login'] = data['last_login'].strftime(
                        "%d-%m-%Y %H:%M:%S") if data['last_login'] else data['last_login']
                    data['start_date'] = data['start_date'].strftime(
                        "%d-%m-%Y %H:%M:%S") if data['start_date'] else data['start_date']

                elif self.user.role == MyUser.EMPLOYE_AGENCE:
                    employe = Employee.objects.get(id=self.user.id)
                    agence = Agence.objects.get(employes__id=self.user.id)
                    data['agence'] = model_to_dict(agence)
                    data['agence']['last_date_cloture'] = data['agence']['last_date_cloture'].strftime(
                        "%d-%m-%Y %H:%M:%S") if data['agence']['last_date_cloture'] else data['agence']['last_date_cloture']
                    data.update(model_to_dict(employe, fields=['id', 'username', 'first_name', 'last_name',
                                                               'role', 'tel', 'email', 'adresse', 'start_date', 'is_active', 'last_login',
                                                               'date_naissance', 'identifiant', 'compte_banquaire']))
                    data['last_login'] = data['last_login'].strftime(
                        "%d-%m-%Y %H:%M:%S") if data['last_login'] else data['last_login']
                    data['start_date'] = data['start_date'].strftime(
                        "%d-%m-%Y %H:%M:%S") if data['start_date'] else data['start_date']

                elif self.user.role == MyUser.AGENT_COMPENSATION:
                    agent = Agent.objects.get(id=self.user.id)
                    data.update(model_to_dict(agent, fields=['id', 'username', 'first_name', 'last_name',
                                                             'role', 'tel', 'email', 'adresse', 'solde', 'start_date', 'is_active', 'last_login',
                                                             'date_naissance', 'identifiant', 'compte_banquaire']))
                    data['last_login'] = data['last_login'].strftime(
                        "%d-%m-%Y %H:%M:%S") if data['last_login'] else data['last_login']
                    data['start_date'] = data['start_date'].strftime(
                        "%d-%m-%Y %H:%M:%S") if data['start_date'] else data['start_date']

                elif self.user.role == MyUser.SYSADMIN:
                    sysadmin = SysAdmin.objects.get(id=self.user.id)
                    data.update(model_to_dict(sysadmin, fields=['id', 'username', 'first_name', 'last_name',
                                                                'role', 'tel', 'email', 'adresse', 'start_date', 'is_active', 'last_login',
                                                                'date_naissance', 'identifiant', 'compte_banquaire']))
                    data['last_login'] = data['last_login'].strftime(
                        "%d-%m-%Y %H:%M:%S") if data['last_login'] else data['last_login']
                    data['start_date'] = data['start_date'].strftime(
                        "%d-%m-%Y %H:%M:%S") if data['start_date'] else data['start_date']

                elif self.user.role == MyUser.VENDOR:
                    vendor = Vendor.objects.get(id=self.user.id)
                    data.update(model_to_dict(vendor, fields=['id', "myId", 'username', 'first_name', 'last_name',
                                                              'role', 'tel', 'solde', "on_hold", 'client', 'email', 'adresse', 'start_date', 'is_active', 'last_login',
                                                              'date_naissance', 'identifiant', 'compte_banquaire']))
                    data['last_login'] = data['last_login'].strftime(
                        "%d-%m-%Y %H:%M:%S") if data['last_login'] else data['last_login']
                    data['start_date'] = data['start_date'].strftime(
                        "%d-%m-%Y %H:%M:%S") if data['start_date'] else data['start_date']

                elif self.user.role == MyUser.CLIENT:
                    client = ClientDigiPay.objects.get(id=self.user.id)
                    data.update(model_to_dict(client, fields=['id', 'username', 'premium', 'first_name', 'last_name',
                                                              'role', 'tel', 'solde', "on_hold", 'client', 'email', 'adresse', 'start_date', 'is_active', 'last_login',
                                                              'date_naissance', 'identifiant', 'compte_banquaire']))
                    data['last_login'] = data['last_login'].strftime(
                        "%d-%m-%Y %H:%M:%S") if data['last_login'] else data['last_login']
                    data['start_date'] = data['start_date'].strftime(
                        "%d-%m-%Y %H:%M:%S") if data['start_date'] else data['start_date']

                elif self.user.role == MyUser.FACTURIER:
                    service = Facturier.objects.get(id=self.user.id)
                    data.update(model_to_dict(service, fields=['id', 'username', 'first_name', 'last_name',
                                                               'role', 'solde', 'email', 'adresse', 'start_date', 'is_active', 'last_login',
                                                               'date_naissance', 'identifiant', 'compte_banquaire']))
                    data['last_login'] = data['last_login'].strftime(
                        "%d-%m-%Y %H:%M:%S") if data['last_login'] else data['last_login']
                    data['start_date'] = data['start_date'].strftime(
                        "%d-%m-%Y %H:%M:%S") if data['start_date'] else data['start_date']

                return data


class ChangePasswordSerializer(serializers.Serializer):
    # update password user
    model = MyUser
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

# compensation serializer ...


class CompensationFullSerializer(serializers.ModelSerializer):
    agence = AgenceFullSerializer()
    agent = Agent_UserSerializer()

    class Meta:
        model = Compensation
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('id', 'username', 'first_name', 'last_name', 'role')

# transfert direct serializer ...


class TransfertDirectFullSerializer(serializers.ModelSerializer):
    # Hide not used attributes in exp et dest ...
    # move to models ??
    expediteur = serializers.SerializerMethodField()
    destinataire = serializers.SerializerMethodField()
    code_secret = serializers.CharField()

    class Meta:
        model = TransfertDirect
        fields = '__all__'

    def get_expediteur(self, instance):
        data = {}
        if instance.expediteur.role == MyUser.CLIENT:
            client = ClientDigiPay.objects.get(id=instance.expediteur.id)
            data = CLientDigipay_ProfilSerializer(client).data
            return data
        elif instance.expediteur.role == MyUser.VENDOR:
            vendor = Vendor.objects.get(id=instance.expediteur.id)
            data = Vendor_ProfilSerializer(vendor).data
            return data
        elif instance.destinataire.role == MyUser.FACTURIER:
            vendor = Facturier.objects.get(id=instance.destinataire.id)
            data = Facturier_ProfilSerializer(vendor).data
            return data
        else:
            return instance.expediteur.id

    def get_destinataire(self, instance):
        data = {}
        if instance.destinataire.role == MyUser.CLIENT:
            client = ClientDigiPay.objects.get(id=instance.destinataire.id)
            data = CLientDigipay_ProfilSerializer(client).data
            return data
        elif instance.destinataire.role == MyUser.VENDOR:
            vendor = Vendor.objects.get(id=instance.destinataire.id)
            data = Vendor_ProfilSerializer(vendor).data
            return data
        elif instance.destinataire.role == MyUser.FACTURIER:
            vendor = Facturier.objects.get(id=instance.destinataire.id)
            data = Facturier_ProfilSerializer(vendor).data
            return data
        else:
            return instance.destinataire.id


class PreTransactionFullSerializer(serializers.ModelSerializer):
    expediteur = serializers.SerializerMethodField()
    code_secret = serializers.CharField()

    class Meta:
        model = PreTransaction
        fields = '__all__'

    def get_expediteur(self, instance):
        data = {}
        if instance.expediteur.role == MyUser.CLIENT:
            client = ClientDigiPay.objects.get(id=instance.expediteur.id)
            data = CLientDigipay_ProfilSerializer(client).data
            return data
        elif instance.expediteur.role == MyUser.VENDOR:
            vendor = Vendor.objects.get(id=instance.expediteur.id)
            data = Vendor_ProfilSerializer(vendor).data
            return data
        else:
            return instance.expediteur.id


# Cagnote Serialiser
class CagnoteFullSerializer(serializers.ModelSerializer):
    nbre_participants = serializers.IntegerField()
    numero_cagnote = serializers.CharField()
    responsable = UserSerializer()
    beneficiaire = UserSerializer()

    class Meta:
        model = Cagnote
        fields = '__all__'


class CagnoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cagnote
        fields = '__all__'


class TransfertCagnoteFullSerializer(serializers.ModelSerializer):
    expediteur = serializers.SerializerMethodField()
    destinataire = serializers.SerializerMethodField()

    def get_expediteur(self, instance):
        data = {}
        if instance.type_transaction == TransfertCagnote.CAGNOTE:
            client = ClientDigiPay.objects.get(id=instance.expediteur)
            data = CLientDigipay_ProfilSerializer(client).data
            return data
        elif instance.type_transaction == TransfertCagnote.RECOLTE or instance.type_transaction == TransfertCagnote.CAGNOTE_ANNULE:
            cagnote = Cagnote.objects.get(id=instance.expediteur)
            data = CagnoteFullSerializer(cagnote).data
            return data
        else:
            return instance.expediteur

    def get_destinataire(self, instance):
        data = {}
        if instance.type_transaction == TransfertCagnote.RECOLTE or instance.type_transaction == TransfertCagnote.CAGNOTE_ANNULE:
            client = ClientDigiPay.objects.get(id=instance.destinataire)
            data = CLientDigipay_ProfilSerializer(client).data
            return data
        elif instance.type_transaction == TransfertCagnote.CAGNOTE:
            cagnote = Cagnote.objects.get(id=instance.destinataire)
            data = CagnoteFullSerializer(cagnote).data
            return data
        else:
            return instance.destinataire

    class Meta:
        model = TransfertCagnote
        fields = '__all__'


class ParticipationCagnoteSerializer(serializers.ModelSerializer):
    participant = UserSerializer()

    class Meta:
        model = ParticipantsCagnote
        fields = '__all__'

# Group payement


class Grp_PayementFullSerializer(serializers.ModelSerializer):
    nbre_beneficiaires = serializers.IntegerField()
    total_montant = serializers.FloatField()
    responsable = UserSerializer()

    class Meta:
        model = GroupPayement
        fields = '__all__'


class Grp_PayementSerializer(serializers.ModelSerializer):

    class Meta:
        model = GroupPayement
        fields = '__all__'

# Beneficiaire grp payement


class BeneficiaresGrpPayementFullSerializer(serializers.ModelSerializer):
    beneficiaire = UserSerializer()
    grp_payement = Grp_PayementFullSerializer()

    class Meta:
        model = BeneficiaresGrpPayement
        fields = '__all__'


class BeneficiaresGrpPayementSerializer(serializers.ModelSerializer):

    class Meta:
        model = BeneficiaresGrpPayement
        fields = '__all__'

# todo List , Update , Get , change pwsd :  ( create : responsable ) , employee , agent
