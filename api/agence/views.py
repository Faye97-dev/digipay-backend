from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.http import JsonResponse, HttpResponse
from .actions import transfert, retrait
from api.models import Agence
#from users.models import Transfert, Transaction, Client_DigiPay, Pre_Transaction, Transfert_Direct
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
        # try:
        agence_destination = Agence.objects.get(
            id=data['agence_destination'])
        result = retrait(agence_destination, data)
        return JsonResponse(result, safe=False, status=201)
    # except:
        # return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)
