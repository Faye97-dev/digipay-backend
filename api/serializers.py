from users.models import Client, Transfert, Compensation, Cloture, Transaction, Notification, PreTransaction
from .models import Agence, Commune
from rest_framework import serializers
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


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


class CompensationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compensation
        fields = '__all__'

# CompensationFullSerializer in users.Serializer ...


'''
class ClotureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cloture
        fields = '__all__'
'''


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = '__all__'


class TransactionFullSerializer(serializers.ModelSerializer):
    #agence = AgenceFullSerializer()
    # to moved ....
    code_transaction = serializers.CharField()

    class Meta:
        model = Transaction
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = '__all__'


class PreTransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = PreTransaction
        fields = '__all__'
