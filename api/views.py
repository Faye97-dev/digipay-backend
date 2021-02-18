
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import requests
from django_filters import rest_framework as filters
from rest_framework import status, generics, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from users.serializers import CompensationFullSerializer, TransfertDirectFullSerializer
from users.models import Transfert
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import *
from users.models import MyUser, Responsable, Employee, Client_DigiPay, Vendor, Transfert_Direct, Notification
from .filters import *
import json
from django.forms.models import model_to_dict
# Create your views here.


class CommuneAPIViews(generics.ListAPIView):
    serializer_class = CommuneSerializer
    permission_classes = [AllowAny]
    queryset = Commune.objects.all()

# agences views


class AgenceListAPIViews(generics.ListAPIView):
    serializer_class = AgenceFullSerializer
    permission_classes = [AllowAny]
    queryset = Agence.objects.all()
    filterset_class = AgenceFilter


class AgenceRetriveAPIViews(generics.RetrieveAPIView):
    serializer_class = AgenceFullSerializer
    permission_classes = [AllowAny]
    queryset = Agence.objects.all()


class AgenceUpdateAPIViews(generics.RetrieveUpdateAPIView):
    serializer_class = AgenceSerializer
    permission_classes = [AllowAny]
    queryset = Agence.objects.all()

# clients views


class ClientViewsets(viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    permission_classes = [AllowAny]
    queryset = Client.objects.all()

# transferts views


class TransfertListAPIViews(generics.ListAPIView):
    serializer_class = TransfertFullSerializer
    permission_classes = [AllowAny]
    queryset = Transfert.objects.all().order_by('-date_creation')
    filterset_class = TransfertFilter


class TransfertCreateAPIViews(generics.CreateAPIView):
    serializer_class = TransfertSerializer
    permission_classes = [AllowAny]
    queryset = Transfert.objects.all()


class TransfertRetriveAPIViews(generics.RetrieveAPIView):
    serializer_class = TransfertFullSerializer
    permission_classes = [AllowAny]
    queryset = Transfert.objects.all()


class TransfertUpdateAPIViews(generics.RetrieveUpdateAPIView):
    serializer_class = TransfertSerializer
    permission_classes = [AllowAny]
    queryset = Transfert.objects.all()


class TransfertDeleteAPIViews(generics.DestroyAPIView):
    serializer_class = TransfertSerializer
    permission_classes = [AllowAny]
    queryset = Transfert.objects.all()

# compensation views


class CompensationListAPIViews(generics.ListAPIView):
    serializer_class = CompensationFullSerializer
    permission_classes = [AllowAny]
    queryset = Compensation.objects.all()
    filterset_class = CompensationFilter


class CompensationCreateAPIViews(generics.CreateAPIView):
    serializer_class = CompensationSerializer
    permission_classes = [AllowAny]
    queryset = Compensation.objects.all()


class CompensationRetriveAPIViews(generics.RetrieveAPIView):
    serializer_class = CompensationFullSerializer
    permission_classes = [AllowAny]
    queryset = Compensation.objects.all()


class CompensationUpdateAPIViews(generics.RetrieveUpdateAPIView):
    serializer_class = CompensationSerializer
    permission_classes = [AllowAny]
    queryset = Compensation.objects.all()


# clotures views
class ClotureViewsets(viewsets.ModelViewSet):
    serializer_class = ClotureSerializer
    permission_classes = [AllowAny]
    queryset = Cloture.objects.all()
    filterset_class = ClotureFilter

# notfication views


class NotificationListAPIViews(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]
    queryset = Notification.objects.all().order_by('-date')
    filterset_class = NotificationFilter

# transactions views


class TransactionListAPIViews(generics.ListAPIView):
    serializer_class = TransactionFullSerializer
    permission_classes = [IsAuthenticated]
    # queryset = Transaction.objects.all().order_by('-date') agence_origine
    filterset_class = TransactionFilter

    def get_queryset(self):
        user = {}
        if self.request.user.role == MyUser.RESPONSABLE_AGENCE:
            user = Responsable.objects.get(id=self.request.user.id)
        elif self.request.user.role == MyUser.EMPLOYE_AGENCE:
            user = Employee.objects.get(id=self.request.user.id)

        if self.request.user.role == MyUser.RESPONSABLE_AGENCE or self.request.user.role == MyUser.EMPLOYE_AGENCE:
            transferts = [item.id for item in list(
                Transfert.objects.filter(agence_origine=user.agence))]
            ###
            retraits = [item.id for item in list(
                Transfert.objects.filter(agence_destination=user.agence))]
            ###
            res = Transaction.objects.filter(
                transaction__id__in=list(set(transferts+retraits))).order_by('-date')
            return res
        elif self.request.user.role == MyUser.CLIENT:
            # handle some cases .... when expediteur is a digiPay client do a transfert and retrait ??
            user = Client_DigiPay.objects.get(id=self.request.user.id)
            retraits_agence = Transfert.objects.filter(expediteur=user.client)
            #print(' before condition ', retraits_agence)
            retraits_agence = [item.id for item in list(
                retraits_agence) if item.agence_destination == item.agence_origine]

            # retraits_agence = [item.id for item in list(
            # Transfert.objects.filter(expediteur=user.client))]
            # transfert_agence = [item.id for item in list(
            #    Transfert.objects.filter(destinataire__id=user.client))]
            ###
            transferts = [item.id for item in list(Transfert_Direct.objects.filter(
                expediteur=user))]
            retraits = [item.id for item in list(Transfert_Direct.objects.filter(
                destinataire=user))]
            print(retraits_agence, transferts, retraits)
            res = Transaction.objects.filter(
                transaction__id__in=list(set(retraits_agence+transferts+retraits))).order_by('-date')
            return res
        else:
            return []

    def list(self, request):
        serializer = self.serializer_class(
            self.filter_queryset(self.get_queryset()), many=True)

        data = []
        for d in serializer.data:
            # if d['type_transaction'] == Transaction.RETRAIT or d['type_transaction'] == Transaction.SUP_3000 or d['type_transaction'] == Transaction.INF_3000:
            # if 'categorie_transaction' in list(d.keys()):
            if d['type_transaction'] in [Transaction.TRANSFERT, Transaction.RETRAIT]:
                transfert = Transfert.objects.get(id=d['transaction'])
                d['transaction'] = TransfertFullSerializer(transfert).data
                data.append(d)
            # elif 'type_transaction' in list(d.keys()):
            elif d['type_transaction'] in [Transaction.COMP_RETRAIT, Transaction.COMP_VERSEMENT]:
                compensation = Compensation.objects.get(
                    id=d['transaction'])
                d['transaction'] = CompensationFullSerializer(
                    compensation).data
                data.append(d)
            elif d['type_transaction'] in [Transaction.ENVOI]:
                transfert = Transfert_Direct.objects.get(
                    id=d['transaction'])
                d['transaction'] = TransfertDirectFullSerializer(
                    transfert).data
                data.append(d)
            else:
                data.append(d)
        return Response(data)


# a corriger ...
class TransactionRetriveAPIViews(generics.RetrieveAPIView):
    serializer_class = TransactionFullSerializer
    permission_classes = [AllowAny]
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
    permission_classes = [AllowAny]
    queryset = Transaction.objects.all()


####
def home(request):
    return render(request, 'index.html')
