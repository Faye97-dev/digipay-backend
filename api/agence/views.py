from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.http import JsonResponse, HttpResponse
from .actions import transfert, retrait, recharge, retrait_par_code
from api.models import Agence
from users.models import Client_DigiPay, Vendor
from users.serializers import ClientDigiPay_UserSerializer, Vendor_UserSerializer
#from .models import *
import json


@csrf_exempt
def agence_transfert(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        print(data)
        try:
            agence_origine = Agence.objects.get(id=data['agence_origine'])
            result = transfert(agence_origine, data)
            return JsonResponse(result, safe=False, status=201)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@csrf_exempt
def agence_retrait(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            agence_destination = Agence.objects.get(
                id=data['agence_destination'])
            result = retrait(agence_destination, data)
            return JsonResponse(result, safe=False, status=201)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@csrf_exempt
def check_byRole_ClientVendor(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            client = list(Client_DigiPay.objects.filter(tel=data['tel']))
            vendor = list(Vendor.objects.filter(tel=data['tel']))
            result = {}
            if len(client) != 0:
                result = ClientDigiPay_UserSerializer(client[0]).data
                result['montant'] = data['montant']
            elif len(vendor) != 0:
                result = Vendor_UserSerializer(vendor[0]).data
                result['montant'] = data['montant']
            else:
                result = {
                    'msg': "le numéro de téléphone n'est pas associé à un compte client ou commerçant !"}

            return JsonResponse(result, safe=False, status=200)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@csrf_exempt
def agence_recharge(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            agence = Agence.objects.get(id=data['agence'])
            result = recharge(agence, data['destinataire'], data['montant'])
            return JsonResponse(result, safe=False, status=201)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@csrf_exempt
def agence_retrait_par_codeConfirmation(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            agence = Agence.objects.get(id=data['agence'])
            result = retrait_par_code(agence, data['pre_transaction'])
            return JsonResponse(result, safe=False, status=201)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)
