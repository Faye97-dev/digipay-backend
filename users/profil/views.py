from django.http import JsonResponse, HttpResponse
from api.models import Agence
from users.models import Client_DigiPay, Vendor, Transfert, Transaction, Pre_Transaction, Transfert_Direct, Client, MyUser, Responsable, Employee, Agent
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
import json


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def valid_vendor_username(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            vendor = Vendor.objects.get(id=data['id'])
            same_username = vendor.username == str(data['username'])
            if same_username:
                print('username non modifier ...')
                return JsonResponse({'valid_username': True}, safe=False, status=200)

            vendor_exist_tel = list(
                Vendor.objects.filter(tel=str(data['username'])))
            client_exist_tel = list(
                Client_DigiPay.objects.filter(tel=str(data['username'])))
            responsable_exist_tel = list(
                Responsable.objects.filter(tel=str(data['username'])))
            employe_exist_tel = list(
                Employee.objects.filter(tel=str(data['username'])))
            agent_exist_tel = list(
                Agent.objects.filter(tel=str(data['username'])))
            ###
            vendor_exist_username = list(
                MyUser.objects.filter(username=str(data['username'])))

            if (len(vendor_exist_username) == 0 and
                len(vendor_exist_tel) == 0 and len(client_exist_tel) == 0 and
                len(responsable_exist_tel) == 0 and len(employe_exist_tel) == 0 and
                    len(agent_exist_tel) == 0):
                return JsonResponse({'valid_username': True}, safe=False, status=200)
            else:
                return JsonResponse({'valid_username': False}, safe=False, status=200)

        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def valid_code_PIN(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            user = MyUser.objects.get(id=data['id'])
            valid_PIN = user.check_password(data['PIN'])
            return JsonResponse({'PIN': valid_PIN}, safe=False, status=200)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)
