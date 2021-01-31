from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import Agence, Commune
from users.models import Client, Transfert, Compensation, Cloture, Transaction


class CommuneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commune
        fields = '__all__'


class AgenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agence
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


class TransfertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfert
        fields = '__all__'


class TransfertFullSerializer(serializers.ModelSerializer):
    agence_origine = AgenceFullSerializer()
    agence_destination = AgenceFullSerializer()
    destinataire = ClientSerializer()
    code_secret = serializers.CharField()

    class Meta:
        model = Transfert
        fields = '__all__'


class CompensationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compensation
        fields = '__all__'

# CompensationFullSerializer in users.Serializer ...


class ClotureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cloture
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = '__all__'


class TransactionFullSerializer(serializers.ModelSerializer):
    #agence = AgenceFullSerializer()
    code_transaction = serializers.CharField()

    class Meta:
        model = Transaction
        fields = '__all__'
