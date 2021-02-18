from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from .models import HOST
from django.http import JsonResponse, HttpResponse
from users.models import Transfert, Transaction, Client_DigiPay, Pre_Transaction
#from .models import *
#from .serializers import TransfertFullSerializer
from users.serializers import ClientDigiPay_UserSerializer
import json


@csrf_exempt
def check_clientDigiPay(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            sender = Client_DigiPay.objects.get(id=data['sender'])
            soldeEnough = True if sender.solde > data['montant'] else False
            ##
            if str(sender.tel) != str(data['tel']):
                client = list(Client_DigiPay.objects.filter(tel=data['tel']))
                result = {'client': data['tel'], 'check': False, 'montant': data['montant'], 'soldeEnough': soldeEnough} if len(
                    client) == 0 else {'client': ClientDigiPay_UserSerializer(client[0]).data, 'check': True,
                                       'montant': data['montant'], 'soldeEnough': soldeEnough}
                print(sender.tel, data['tel'])
            else:
                result = {
                    'msg': 'le numero de telephone du client est similaire au numero du compte utilisateur !'}
            return JsonResponse(result, safe=False, status=200)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)
