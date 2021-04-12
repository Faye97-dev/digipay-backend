from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.http import JsonResponse, HttpResponse
from .actions import transfert, retrait, recharge, retrait_par_code, confirmer_compensation, annuler_compensation
from api.models import Agence
from users.models import Client_DigiPay, Vendor, Transfert, Transaction, Pre_Transaction, Transfert_Direct, Client
from users.serializers import ClientDigiPay_UserSerializer, Vendor_UserSerializer
from api.serializers import TransfertFullSerializer
from users.serializers import PreTransactionFullSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
import json


# @csrf_exempt
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
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


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
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


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
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


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
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


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
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


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def transactions_a_retirer(request):
    # sort data by  - date
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            if not data['tel'].isdigit():
                return JsonResponse([], safe=False, status=200)

            agence = Agence.objects.get(id=data['agence_destination'])

            retraits = Transfert.objects.filter(agence_destination=agence,
                                                destinataire__tel=data['tel'], status=Transfert.NOT_WITHDRAWED).order_by('-date_creation')
            '''
            retraits = Transfert.objects.filter(
                destinataire__tel=data['tel'], status=Transfert.NOT_WITHDRAWED).order_by('-date_creation')
            '''
            pre_retraits = Pre_Transaction.objects.filter(
                type_transaction=Pre_Transaction.RETRAIT, status=Pre_Transaction.TO_VALIDATE, destinataire=data['tel']).order_by('-date_creation')
            #print(retraits, pre_retraits)

            result = TransfertFullSerializer(
                retraits, many=True).data + PreTransactionFullSerializer(pre_retraits, many=True).data
            return JsonResponse(result, safe=False, status=200)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def check_existant_tel(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            client = list(Client.objects.filter(tel=str(data['tel'])))
            result = {'valid_tel': True} if len(client) == 0 else {
                'valid_tel': False}
            return JsonResponse(result, safe=False, status=200)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def valid_compensation(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            agence = Agence.objects.get(id=data['agence'])
            if data['confirm']:
                result = confirmer_compensation(
                    agence, data['transaction'], data['notif'])
            if data['confirm'] == False:
                result = annuler_compensation(
                    agence, data['transaction'], data['notif'])
            return JsonResponse(result, safe=False, status=201)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)
