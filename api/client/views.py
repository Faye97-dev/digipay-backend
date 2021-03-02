from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.http import JsonResponse, HttpResponse
from .actions import retrait, payement, achat_credit
from api.models import Agence
from users.models import Client_DigiPay, Vendor, MyUser, Pre_Transaction, TransactionModel
from users.serializers import PreTransactionFullSerializer
#from .models import *
import json


@csrf_exempt
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


@csrf_exempt
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


@csrf_exempt
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


@csrf_exempt
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
