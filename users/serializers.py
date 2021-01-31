from django.forms.models import model_to_dict
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from users.models import MyUser, Agent, Employee, Responsable, Compensation
from api.models import Agence
from api.serializers import AgenceSerializer, AgenceFullSerializer


# register users
class Agent_UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = Agent
        fields = ('username', 'first_name', 'last_name',
                  'role', 'password', 'tel', 'email', 'adresse')
        extra_kwargs = {'password': {'write_only': True}}

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

# login


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
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
            data.update(model_to_dict(responsable, fields=['id', 'username', 'first_name', 'last_name',
                                                           'role', 'tel', 'email', 'adresse', 'start_date', 'is_active', 'last_login']))
        elif self.user.role == MyUser.EMPLOYE_AGENCE:
            employe = Employee.objects.get(id=self.user.id)
            agence = Agence.objects.get(employes__id=self.user.id)
            data['agence'] = model_to_dict(agence)
            data.update(model_to_dict(employe, fields=['id', 'username', 'first_name', 'last_name',
                                                       'role', 'tel', 'email', 'adresse', 'start_date', 'is_active', 'last_login']))
        elif self.user.role == MyUser.AGENT_COMPENSATION:
            agent = Agent.objects.get(id=self.user.id)
            data.update(model_to_dict(agent, fields=['id', 'username', 'first_name', 'last_name',
                                                     'role', 'tel', 'email', 'adresse', 'start_date', 'is_active', 'last_login']))

        return data


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
        fields = '__all__'

# todo List , Update , Get , change pwsd :  ( create : responsable ) , employee , agent
