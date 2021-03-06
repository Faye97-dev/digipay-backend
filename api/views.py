
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import requests
from django_filters import rest_framework as filters
from rest_framework import status, generics, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from users.serializers import CompensationFullSerializer, TransfertDirectFullSerializer, CagnoteSerializer, TransfertCagnoteFullSerializer, Grp_PayementFullSerializer, Grp_PayementSerializer, BeneficiaresGrpPayementSerializer, BeneficiaresGrpPayementFullSerializer
from users.models import Transfert, GroupPayement, BeneficiaresGrpPayement
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import *
from users.models import MyUser, Responsable, Employee, ClientDigiPay, Vendor, TransfertDirect, Notification, Agent, ParticipantsCagnote, Cagnote, TransfertCagnote
from .filters import *
from django.forms.models import model_to_dict
from .service import transactionListByUser, compensationsListByUser, paiement_masse_total
import json

# Create your views here.


class CommuneAPIViews(generics.ListAPIView):
    serializer_class = CommuneSerializer
    permission_classes = [AllowAny]
    queryset = Commune.objects.all()

# agences views


class AgenceListAPIViews(generics.ListAPIView):
    serializer_class = AgenceFullSerializer
    permission_classes = [IsAuthenticated]
    queryset = Agence.objects.all()
    filterset_class = AgenceFilter


class AgenceRetriveAPIViews(generics.RetrieveAPIView):
    serializer_class = AgenceFullSerializer
    permission_classes = [IsAuthenticated]
    queryset = Agence.objects.all()


class AgenceUpdateAPIViews(generics.RetrieveUpdateAPIView):
    serializer_class = AgenceSerializer
    permission_classes = [IsAuthenticated]
    queryset = Agence.objects.all()

# clients views


class ClientViewsets(viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    queryset = Client.objects.all()

# transferts views


class TransfertListAPIViews(generics.ListAPIView):
    serializer_class = TransfertFullSerializer
    permission_classes = [IsAuthenticated]
    queryset = Transfert.objects.all().order_by('-date_creation')
    filterset_class = TransfertFilter


class TransfertCreateAPIViews(generics.CreateAPIView):
    serializer_class = TransfertSerializer
    permission_classes = [IsAuthenticated]
    queryset = Transfert.objects.all()


class TransfertRetriveAPIViews(generics.RetrieveAPIView):
    serializer_class = TransfertFullSerializer
    permission_classes = [IsAuthenticated]
    queryset = Transfert.objects.all()


class TransfertUpdateAPIViews(generics.RetrieveUpdateAPIView):
    serializer_class = TransfertSerializer
    permission_classes = [IsAuthenticated]
    queryset = Transfert.objects.all()


class TransfertDeleteAPIViews(generics.DestroyAPIView):
    serializer_class = TransfertSerializer
    permission_classes = [IsAuthenticated]
    queryset = Transfert.objects.all()

# compensation views


class CompensationListAPIViews(generics.ListAPIView):
    serializer_class = CompensationFullSerializer
    permission_classes = [IsAuthenticated]
    queryset = Compensation.objects.all()
    filterset_class = CompensationFilter


class CompensationCreateAPIViews(generics.CreateAPIView):
    serializer_class = CompensationSerializer
    permission_classes = [IsAuthenticated]
    queryset = Compensation.objects.all()


class CompensationRetriveAPIViews(generics.RetrieveAPIView):
    serializer_class = CompensationFullSerializer
    permission_classes = [IsAuthenticated]
    queryset = Compensation.objects.all()


class CompensationUpdateAPIViews(generics.RetrieveUpdateAPIView):
    serializer_class = CompensationSerializer
    permission_classes = [IsAuthenticated]
    queryset = Compensation.objects.all()


# clotures views
'''
class ClotureViewsets(viewsets.ModelViewSet):
    serializer_class = ClotureSerializer
    permission_classes = [IsAuthenticated]
    queryset = Cloture.objects.all()
    filterset_class = ClotureFilter
'''
# notfication views


class NotificationListAPIViews(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    #queryset = Notification.objects.all().order_by('-date')
    #filterset_class = NotificationFilter

    def get_queryset(self):
        res = Notification.objects.filter(
            user=self.request.user).order_by('-date')
        return res

    def list(self, request):
        # serializer = self.serializer_class(
        #    self.filter_queryset(self.get_queryset()), many=True)
        serializer = self.serializer_class(self.get_queryset(), many=True)

        data = []
        for d in serializer.data:
            if d['status'] in [Notification.DEMANDE_COMPENSATION, Notification.COMPENSATION]:
                compensation = Compensation.objects.get(
                    id=d['transaction'])
                d['transaction'] = CompensationFullSerializer(
                    compensation).data
                data.append(d)
            elif d['status'] in [Notification.DEMANDE_PAIEMENT]:
                pre_transaction = PreTransaction.objects.get(
                    id=d['transaction'])
                d['transaction'] = PreTransactionSerializer(
                    pre_transaction).data
                data.append(d)
            else:
                data.append(d)
        return Response(data)


class NotificationUpdateAPIViews(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all().order_by('-date')

# transactions views


class TransactionListAPIViews(generics.ListAPIView):
    serializer_class = TransactionFullSerializer
    permission_classes = [IsAuthenticated]
    # queryset = Transaction.objects.all().order_by('-date') agence_origine
    filterset_class = TransactionFilter

    def get_queryset(self):
        return transactionListByUser(self.request.user)

    def list(self, request):
        serializer = self.serializer_class(
            self.filter_queryset(self.get_queryset()), many=True)

        data = []
        for d in serializer.data:
            if d['type_transaction'] in [Transaction.TRANSFERT, Transaction.RETRAIT, Transaction.RECHARGE]:
                transfert = Transfert.objects.get(id=d['transaction'])
                d['transaction'] = TransfertFullSerializer(transfert).data
                data.append(d)
            elif d['type_transaction'] in [Transaction.COMP_RETRAIT, Transaction.COMP_VERSEMENT]:
                compensation = Compensation.objects.get(
                    id=d['transaction'])
                d['transaction'] = CompensationFullSerializer(
                    compensation).data
                data.append(d)
            elif d['type_transaction'] in [Transaction.ENVOI, Transaction.PAIEMENT, Transaction.REMBOURSEMENT, Transaction.PAIEMENT_MASSE, Transaction.PAIEMENT_FACTURE]:
                transfert = TransfertDirect.objects.get(
                    id=d['transaction'])
                d['transaction'] = TransfertDirectFullSerializer(
                    transfert).data
                if transfert.expediteur.id == request.user.id and d['type_transaction'] == Transaction.PAIEMENT_MASSE:
                    d['transaction']['total'] = paiement_masse_total(
                        transfert.numero_grp_payement)
                else:
                    d['transaction']['total'] = None
                data.append(d)
            elif d['type_transaction'] in [Transaction.CAGNOTE, Transaction.RECOLTE, Transaction.CAGNOTE_ANNULE]:
                transfert = TransfertCagnote.objects.get(
                    id=d['transaction'])
                d['transaction'] = TransfertCagnoteFullSerializer(
                    transfert).data
                data.append(d)
            else:
                data.append(d)

        # for d in data[:10]:
        #    print(json.dumps(d) + "\n")

        '''
        file_ = open("dummy_data.txt", "w")
        for e in data:
            file_.write(json.dumps(e) + "\n")
        file_.close()

        with open("./dummy_data.txt", 'w') as f:
            for d in data:
                f.write(json.dumps(d))
                # print(json.dumps(d))
        '''
        return Response(data)


class TransactionCompensationListAPIViews(generics.ListAPIView):
    serializer_class = TransactionFullSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TransactionFilter

    def get_queryset(self):
        return compensationsListByUser(self.request.user)

    def list(self, request):
        serializer = self.serializer_class(
            self.filter_queryset(self.get_queryset()), many=True)

        data = []
        for d in serializer.data:
            if d['type_transaction'] in [Transaction.COMP_RETRAIT, Transaction.COMP_VERSEMENT]:
                compensation = Compensation.objects.get(
                    id=d['transaction'])
                d['transaction'] = CompensationFullSerializer(
                    compensation).data
                data.append(d)
            else:
                data.append(d)

        # for d in data[:5]:
        #    print(json.dumps(d) + "\n")

        return Response(data)


class TransactionRetriveAPIViews(generics.RetrieveAPIView):
    # a corriger bugs existant...
    serializer_class = TransactionFullSerializer
    permission_classes = [IsAuthenticated]
    queryset = Transaction.objects

    def get(self, request, pk):
        serializer = self.serializer_class(
            self.get_queryset().get(id=pk), many=False)

        d = serializer.data
        if 'categorie_transaction' in list(d.keys()):
            transfert = Transfert.objects.get(id=d['transaction'])
            d['transaction'] = TransfertFullSerializer(transfert).data
            return Response(d)
        elif 'type_transaction' in list(d.keys()):
            compensation = Compensation.objects.get(id=d['transaction'])
            d['transaction'] = CompensationFullSerializer(compensation).data
            return Response(d)
        else:
            return Response(d)


class TransactionCreateAPIViews(generics.CreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    queryset = Transaction.objects.all()


# group payement views
class Grp_PayementListAPIViews(generics.ListAPIView):
    serializer_class = Grp_PayementFullSerializer
    permission_classes = [IsAuthenticated]
    # queryset = GroupPayement.objects.all().order_by('-date')

    def get_queryset(self):
        if self.request.user.role == MyUser.CLIENT:
            res = GroupPayement.objects.filter(
                responsable=self.request.user).order_by('-date')
            return res
        else:
            return []


class Grp_PayementCreateAPIViews(generics.CreateAPIView):
    serializer_class = Grp_PayementSerializer
    permission_classes = [IsAuthenticated]
    queryset = GroupPayement.objects.all()

    def create(self, request, *args, **kwargs):
        response = super(Grp_PayementCreateAPIViews,
                         self).create(request, *args, **kwargs)
        response.status = status.HTTP_200_OK
        temp = GroupPayement.objects.get(id=response.data['id'])
        response.data = Grp_PayementFullSerializer(temp).data
        return response


class Grp_PayementDeleteAPIViews(generics.DestroyAPIView):
    serializer_class = Grp_PayementSerializer
    permission_classes = [IsAuthenticated]
    queryset = GroupPayement.objects.all()


'''
class ParticipationCagnoteListAPIViews(generics.ListAPIView):
    serializer_class = ParticipationCagnoteFullSerializer
    permission_classes = [IsAuthenticated]
    # queryset = Transaction.objects.all().order_by('-date')

    def get_queryset(self):
        return participationCagnoteListByUser(self.request.user)
'''

'''
class CagnoteCreateAPIViews(generics.CreateAPIView):
    serializer_class = CagnoteSerializer
    permission_classes = [IsAuthenticated]
    queryset = Cagnote.objects.all()
'''
####


def home(request):
    return render(request, 'index.html')
