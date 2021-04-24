from django.forms.models import model_to_dict
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from users.models import MyUser, Agent, Employee, Responsable, Compensation, Client_DigiPay, Client, Vendor, Transfert_Direct, Pre_Transaction, SysAdmin
from api.models import Agence
from api.serializers import AgenceSerializer, AgenceFullSerializer
import random
from datetime import datetime


def random_with_N_digits(n):
    start = 10**(n-1)
    end = (10**n) - 1
    random.seed(datetime.now())
    res = random.randint(start, end)
    return res

# register users


class Agent_UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = Agent
        fields = ('id', 'username', 'first_name', 'last_name',
                  'role', 'password', 'tel', 'email', 'adresse', 'start_date', 'is_active', 'last_login')
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
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = SysAdmin
        fields = ('id', 'username', 'first_name', 'last_name',
                  'role', 'password', 'tel', 'email', 'adresse', 'start_date', 'is_active', 'last_login')
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
    password = serializers.CharField(min_length=8, write_only=True)

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
                  'role', 'password', 'tel', 'email', 'adresse', 'agence', 'start_date', 'is_active', 'last_login')
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
    password = serializers.CharField(min_length=8, write_only=True)
    agence = AgenceSerializer()

    class Meta:
        model = Responsable
        fields = ('id', 'username', 'first_name', 'last_name',
                  'role', 'password', 'tel', 'email', 'adresse', 'agence', 'start_date', 'is_active', 'last_login')
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
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = Client_DigiPay
        fields = ('id', 'username', 'first_name', 'last_name',
                  'role', 'password', 'tel', 'email', 'adresse', 'solde', "on_hold", 'client', 'start_date', 'is_active', 'last_login')
        extra_kwargs = {'password': {'write_only': True},
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
        model = Client_DigiPay
        fields = ('id', 'username', 'first_name', 'role',
                  'last_name', 'tel', 'email', 'adresse')


class Vendor_UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    tel = serializers.CharField(required=True)
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = Vendor
        fields = ('id', "myId", 'username', 'first_name', 'last_name',
                  'role', 'password', 'tel', 'email', 'adresse', 'solde', "on_hold", 'client', 'start_date', 'is_active', 'last_login')
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
                  'last_name', 'tel', 'email', 'adresse')


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    # login
    #name = serializers.CharField(required=False)

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        # Add extra responses here
        if self.user.role == MyUser.RESPONSABLE_AGENCE:
            responsable = Responsable.objects.get(id=self.user.id)
            agence = Agence.objects.get(responsable__id=self.user.id)
            data['agence'] = model_to_dict(agence)
            data['agence']['last_date_cloture'] = data['agence']['last_date_cloture'].strftime(
                "%d-%m-%Y %H:%M:%S") if data['agence']['last_date_cloture'] else data['agence']['last_date_cloture']
            # print(data['agence']['last_date_cloture'])
            data.update(model_to_dict(responsable, fields=['id', 'username', 'first_name', 'last_name',
                                                           'role', 'tel', 'email', 'adresse', 'start_date', 'is_active', 'last_login']))
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
                                                       'role', 'tel', 'email', 'adresse', 'start_date', 'is_active', 'last_login']))
            data['last_login'] = data['last_login'].strftime(
                "%d-%m-%Y %H:%M:%S") if data['last_login'] else data['last_login']
            data['start_date'] = data['start_date'].strftime(
                "%d-%m-%Y %H:%M:%S") if data['start_date'] else data['start_date']

        elif self.user.role == MyUser.AGENT_COMPENSATION:
            agent = Agent.objects.get(id=self.user.id)
            data.update(model_to_dict(agent, fields=['id', 'username', 'first_name', 'last_name',
                                                     'role', 'tel', 'email', 'adresse', 'start_date', 'is_active', 'last_login']))
            data['last_login'] = data['last_login'].strftime(
                "%d-%m-%Y %H:%M:%S") if data['last_login'] else data['last_login']
            data['start_date'] = data['start_date'].strftime(
                "%d-%m-%Y %H:%M:%S") if data['start_date'] else data['start_date']

        elif self.user.role == MyUser.SYSADMIN:
            sysadmin = SysAdmin.objects.get(id=self.user.id)
            data.update(model_to_dict(sysadmin, fields=['id', 'username', 'first_name', 'last_name',
                                                        'role', 'tel', 'email', 'adresse', 'start_date', 'is_active', 'last_login']))
            data['last_login'] = data['last_login'].strftime(
                "%d-%m-%Y %H:%M:%S") if data['last_login'] else data['last_login']
            data['start_date'] = data['start_date'].strftime(
                "%d-%m-%Y %H:%M:%S") if data['start_date'] else data['start_date']

        elif self.user.role == MyUser.VENDOR:
            vendor = Vendor.objects.get(id=self.user.id)
            data.update(model_to_dict(vendor, fields=['id', "myId", 'username', 'first_name', 'last_name',
                                                      'role', 'tel', 'solde', "on_hold", 'client', 'email', 'adresse', 'start_date', 'is_active', 'last_login']))
            data['last_login'] = data['last_login'].strftime(
                "%d-%m-%Y %H:%M:%S") if data['last_login'] else data['last_login']
            data['start_date'] = data['start_date'].strftime(
                "%d-%m-%Y %H:%M:%S") if data['start_date'] else data['start_date']

        elif self.user.role == MyUser.CLIENT:
            client = Client_DigiPay.objects.get(id=self.user.id)
            data.update(model_to_dict(client, fields=['id', 'username', 'first_name', 'last_name',
                                                      'role', 'tel', 'solde', "on_hold", 'client', 'email', 'adresse', 'start_date', 'is_active', 'last_login']))
            data['last_login'] = data['last_login'].strftime(
                "%d-%m-%Y %H:%M:%S") if data['last_login'] else data['last_login']
            data['start_date'] = data['start_date'].strftime(
                "%d-%m-%Y %H:%M:%S") if data['start_date'] else data['start_date']
        return data


class ChangePasswordSerializer(serializers.Serializer):
    # update password user
    model = MyUser
    """
    Serializer for password change endpoint.
    """
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


class PreTransactionFullSerializer(serializers.ModelSerializer):
    expediteur = serializers.SerializerMethodField()
    code_secret = serializers.CharField()

    class Meta:
        model = Pre_Transaction
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


# todo List , Update , Get , change pwsd :  ( create : responsable ) , employee , agent
