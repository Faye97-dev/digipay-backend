from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.http import JsonResponse, HttpResponse
from .actions import retrait, payement, achat_credit
from api.models import *
from users.models import Client_DigiPay, Vendor, MyUser, TransactionModel, Transfert, Transaction, Pre_Transaction, Transfert_Direct, Client
from users.serializers import PreTransactionFullSerializer
from api.serializers import TransfertFullSerializer
from users.serializers import PreTransactionFullSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
import json


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def random_code_retrait(request):
    # for vendor and client
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            if data['role'] == MyUser.CLIENT:
                user = Client_DigiPay.objects.get(id=data['id'])
            elif data['role'] == MyUser.VENDOR:
                user = Vendor.objects.get(id=data['id'])
            else:
                result = {'msg': "Json est invalid !"}
                return JsonResponse(result, safe=False, status=400)

            result = retrait(user, data['montant'])
            return JsonResponse(result, safe=False, status=201)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def check_codePayement(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            pre_transaction = Pre_Transaction.objects.filter(
                code_secret=data['code'], status=TransactionModel.TO_VALIDATE)
            if len(list(pre_transaction)) != 0:
                result = PreTransactionFullSerializer(pre_transaction[0]).data
                return JsonResponse(result, safe=False, status=200)
            else:
                return JsonResponse({'msg': "Ce code n'est pas associé a un paiement ou le code est deja confirmer !"}, safe=False, status=200)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def client_payement(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            client = Client_DigiPay.objects.get(id=data['client'])
            result = payement(client, data['pre_transaction'])
            return JsonResponse(result, safe=False, status=201)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def client_achat_credit(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            client = Client_DigiPay.objects.get(id=data['client'])
            result = achat_credit(client, data['tel'], data['montant'])
            return JsonResponse(result, safe=False, status=201)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


# need to perform this part move it to client folder
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def client_digiPay_envoie(request):
    # handle case if number is a vendor
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            if 'client_destinataire' in data.keys():
                client = Client_DigiPay.objects.get(id=data['client_origine'])
                result = client.envoyer(
                    data['client_destinataire'], data['montant'])
                return JsonResponse(result, safe=False, status=201)
            elif 'tel' in data.keys():
                client = Client_DigiPay.objects.get(id=data['client_origine'])
                result = client.envoyer_par_sms(
                    data['tel'], data['montant'])

                return JsonResponse(result, safe=False, status=201)
            else:
                return JsonResponse({'msg': ' Json data invalid !'}, safe=False, status=400)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def client_parSmsRetrait(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            pre_transaction = Pre_Transaction.objects.get(
                id=data['pre_transaction'])
            result = pre_transaction.client_retrait(
                data['agence_destination'], data['nom_destinataire'])
            return JsonResponse(result, safe=False, status=201)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


'''
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def hello_world(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        print(data, ' hhhhhhh')
        return JsonResponse({'msg': "Ce code n'est pas associé a un paiement ou le code est deja confirmer !"}, safe=False, status=200)
    else:
        return HttpResponse(status=405)
'''
