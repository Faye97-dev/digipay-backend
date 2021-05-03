from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.http import JsonResponse, HttpResponse
from .actions import retrait, payement, achat_credit, fast_payement, participer_cagnote, cloturer_cagnote
from api.models import *
from users.models import Client_DigiPay, Vendor, MyUser, TransactionModel, Transfert, Transaction, Pre_Transaction, Transfert_Direct, Client, Cagnote, Participants_Cagnote
from users.serializers import PreTransactionFullSerializer, Vendor_UserSerializer, CagnoteFullSerializer
from api.serializers import TransfertFullSerializer
from users.serializers import PreTransactionFullSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from api.service import participationCagnoteListByUser
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
                code_secret=data['code'], status=TransactionModel.TO_VALIDATE, type_transaction=Pre_Transaction.PAIEMENT)
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
def client_check_VendorId(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            commercant = Vendor.objects.filter(myId=data['code'])
            if len(list(commercant)) != 0:
                result = Vendor_UserSerializer(commercant[0]).data
                return JsonResponse(result, safe=False, status=200)
            else:
                return JsonResponse({'msg': "Aucun commerçant n'est pas associé a ce numéro d'identification !"}, safe=False, status=200)
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
def client_fast_payement(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            client = Client_DigiPay.objects.get(id=data['client'])
            commercant = Vendor.objects.get(id=data['vendor'])
            result = fast_payement(
                client, commercant, data['montant'], data['label'])
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


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def client_digiPay_envoie(request):
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


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def getCagnoteList(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            user = MyUser.objects.get(id=data['id'])
            participations = participationCagnoteListByUser(user)
            cagnotes_inscrits = [item.cagnote.id for item in participations]
            ###
            mes_cagnotes = Cagnote.objects.filter(
                responsable=user)
            # .order_by('-date')
            mes_cagnotes = [
                cagnote.id for cagnote in mes_cagnotes if cagnote.id not in cagnotes_inscrits]

            ###
            all_cagnotes = mes_cagnotes + cagnotes_inscrits
            all_cagnotes = Cagnote.objects.filter(
                id__in=all_cagnotes).order_by('-date')

            result = []
            for c in all_cagnotes:
                temp = {}
                temp['cagnote'] = CagnoteFullSerializer(c).data
                if c.id in cagnotes_inscrits:
                    p = Participants_Cagnote.objects.get(
                        cagnote=c, participant=user)
                    temp['participation'] = {
                        'montant': p.montant, 'date': p.date.strftime('%d-%m-%Y %H:%M:%S')}
                else:
                    temp['participation'] = None
                result.append(temp)

            return JsonResponse(result, safe=False, status=200)

        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def createCagnote(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            client = Client_DigiPay.objects.get(id=data['client'])
            cagnote = Cagnote(
                nom=data['nom'], objectif=data['objectif'], motif=data['motif'], responsable=client)
            cagnote.save()

            result = {}
            result['cagnote'] = CagnoteFullSerializer(cagnote).data
            result['participation'] = None

            return JsonResponse(result, safe=False, status=201)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def check_cagnote_byId(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            cagnote = [c for c in Cagnote.objects.all() if c.numero_cagnote ==
                       data['numero_cagnote']]
            user = MyUser.objects.get(id=data['id'])
            if len(cagnote) != 0:
                result = CagnoteFullSerializer(cagnote[0]).data
                if not result["actif"]:
                    return JsonResponse({'msg': " Cette cagnote n'est plus actif !"}, safe=False, status=200)
                elif result["responsable"]['id'] == user.id:
                    return JsonResponse({'msg': " Vous etes responsable de cette cagnote , pour faire un don aller vers la liste des cagnotes !"}, safe=False, status=200)
                else:
                    participants = Participants_Cagnote.objects.filter(
                        cagnote=cagnote[0], participant=user)
                    if len(list(participants)) != 0:
                        return JsonResponse({'msg': " Vous etes deja paticipant a cette cagnote !"}, safe=False, status=200)
                    else:
                        return JsonResponse(result, safe=False, status=200)
            else:
                return JsonResponse({'msg': "Cet identifiant n'est pas associé a une cagnote !"}, safe=False, status=200)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def client_participer_cagnote(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            cagnote = Cagnote.objects.get(id=data['cagnote'])
            client = Client_DigiPay.objects.get(id=data['client'])
            result = participer_cagnote(client, cagnote, data['montant'])
            return JsonResponse(result, safe=False, status=201)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def client_cloturer_cagnote(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            cagnote = Cagnote.objects.get(id=data['cagnote'])
            client = Client_DigiPay.objects.get(id=data['client'])
            result = cloturer_cagnote(client, cagnote)
            return JsonResponse(result, safe=False, status=201)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)
