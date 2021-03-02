from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.http import JsonResponse, HttpResponse
from .actions import code_payement, payement
from api.models import Agence
from users.models import Client_DigiPay, Vendor, MyUser, Pre_Transaction, TransactionModel
from users.serializers import PreTransactionFullSerializer
#from .models import *
import json


@csrf_exempt
def random_code_payement(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            vendor = Vendor.objects.get(id=data['id'])
            result = code_payement(vendor, data['montant'])
            return JsonResponse(result, safe=False, status=201)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@csrf_exempt
def check_codePayement_vendor(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            pre_transaction = Pre_Transaction.objects.filter(
                code_secret=data['code'], status=TransactionModel.TO_VALIDATE)
            if len(list(pre_transaction)) != 0:
                if pre_transaction[0].expediteur.id != data['vendorId']:
                    result = PreTransactionFullSerializer(
                        pre_transaction[0]).data
                    return JsonResponse(result, safe=False, status=200)
                else:
                    return JsonResponse({'msg': "Ce code est générer par vous même !"}, safe=False, status=200)
            else:
                return JsonResponse({'msg': "Ce code n'est pas associé a un paiement ou le code est deja confirmer !"}, safe=False, status=200)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@csrf_exempt
def vendor_payement(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            vendor = Vendor.objects.get(id=data['vendor'])
            result = payement(vendor, data['pre_transaction'])
            return JsonResponse(result, safe=False, status=201)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)
