from django_filters import rest_framework as filters
from users.models import Transfert, Compensation, Transaction, Cloture, Client
from .models import Agence


class ClientFilter(filters.FilterSet):

    class Meta:
        model = Client
        fields = ['tel']


class TransfertFilter(filters.FilterSet):
    #min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    #max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')
    #type_agence = filters.CharFilter(field_name='relationship__destinataire', lookup_expr='exact')
    tel = filters.CharFilter(
        field_name='destinataire__tel', lookup_expr='exact')

    class Meta:
        model = Transfert
        fields = ['categorie_transaction', 'status', 'expediteur', 'destinataire', 'tel',
                  'agence_origine', 'agence_destination', 'is_edited', 'user_created', 'user_edited']


class CompensationFilter(filters.FilterSet):
    class Meta:
        model = Compensation
        fields = ['type_transaction', 'status', 'agent',
                  'agence', 'is_edited', 'user_created', 'user_edited']


class TransactionFilter(filters.FilterSet):
    min_date = filters.DateTimeFilter(field_name="date", lookup_expr='gte')
    max_date = filters.DateTimeFilter(field_name="date", lookup_expr='lte')

    class Meta:
        model = Transaction
        fields = ['agence', 'type_transaction', 'categorie_transaction',
                  'min_date', 'max_date']


class AgenceFilter(filters.FilterSet):

    class Meta:
        model = Agence
        fields = ['commune', 'type_agence',
                  'active']


class ClotureFilter(filters.FilterSet):
    min_date = filters.DateTimeFilter(field_name="date", lookup_expr='gte')
    max_date = filters.DateTimeFilter(field_name="date", lookup_expr='lte')

    class Meta:
        model = Cloture
        fields = ['agence', 'user',
                  'min_date', 'max_date']

# todo employe , agent , responsable
