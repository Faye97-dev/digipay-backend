import json
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from api.serializers import TransactionFullSerializer
from users.serializers import PreTransactionFullSerializer, TransfertDirectFullSerializer, Vendor_UserSerializer
from users.models import Client_DigiPay, Vendor, MyUser, Pre_Transaction, TransactionModel, Transaction, Transfert_Direct
from api.models import Agence
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.http import JsonResponse, HttpResponse
from .actions import code_payement, payement, fast_payement, remboursement, annuler_livraison_client, confirmer_livraison_client, confirmer_livraison_vendor, annuler_livraison_vendor


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def random_code_payement(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            vendor = Vendor.objects.get(id=data['id'])
            result = code_payement(
                vendor, data['montant'], data['livraison'], data['label'], data['delai'])
            return JsonResponse(result, safe=False, status=201)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def check_codePayement_vendor(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            pre_transaction = Pre_Transaction.objects.filter(
                code_secret=data['code'], status=TransactionModel.TO_VALIDATE, type_transaction=Pre_Transaction.PAIEMENT)
            if len(list(pre_transaction)) != 0:
                if pre_transaction[0].expediteur.id != data['vendorId']:
                    # if not pre_transaction[0].livraison:
                    result = PreTransactionFullSerializer(
                        pre_transaction[0]).data
                    return JsonResponse(result, safe=False, status=200)
                else:
                    return JsonResponse({'msg': "Ce code de payement est générer par vous même !"}, safe=False, status=200)
            else:
                return JsonResponse({'msg': "Ce code n'est pas associé a un paiement ou le code est deja confirmer !"}, safe=False, status=200)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def vendor_fast_payement(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            commercant_client = Vendor.objects.get(id=data['client'])
            commercant = Vendor.objects.get(id=data['vendor'])
            result = fast_payement(
                commercant_client, commercant, data['montant'], data['label'])
            return JsonResponse(result, safe=False, status=201)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
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


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def vendor_check_VendorId(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            commercant = Vendor.objects.filter(myId=data['code'])
            if len(list(commercant)) != 0:
                if commercant[0].id != data['vendorId']:
                    result = Vendor_UserSerializer(commercant[0]).data
                    return JsonResponse(result, safe=False, status=200)
                else:
                    return JsonResponse({'msg': "Ce code commerçant est le votre !"}, safe=False, status=200)
            else:
                return JsonResponse({'msg': "Aucun commerçant n'est associé avec ce code !"}, safe=False, status=200)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def check_codeTransaction(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            vendor = MyUser.objects.get(id=data['vendor'])
            transaction = list(Transaction.objects.filter(
                type_transaction=Transaction.PAIEMENT, transaction__status=TransactionModel.COMFIRMED))

            # valider le num de la transaction et l'auteur de la transaction
            transaction = [
                item for item in transaction if item.code_transaction == data['numero_transaction'] and
                Transfert_Direct.objects.get(id=item.transaction.id).destinataire == vendor]
            # transaction
            if len(transaction) == 0:
                # todo handle msg by case
                return JsonResponse({'msg': "Ce code de transaction n'est pas associé a un paiement ou vous êtes pas l'auteur de la transaction !"}, safe=False, status=200)
            else:
                transaction = transaction[0]

            result = TransactionFullSerializer(transaction).data
            transfert = Transfert_Direct.objects.get(
                id=transaction.transaction.id)
            result['transaction'] = TransfertDirectFullSerializer(
                transfert).data
            return JsonResponse(result, safe=False, status=201)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def vendor_payback(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            vendor = Vendor.objects.get(id=data['vendor'])
            result = remboursement(vendor, data['transaction'])
            return JsonResponse(result, safe=False, status=201)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def livraison_client(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            if data['confirm']:
                result = confirmer_livraison_client(data['transaction'])
                return JsonResponse(result, safe=False, status=201)
            elif data['confirm'] == False:
                result = annuler_livraison_client(data['transaction'])
                return JsonResponse(result, safe=False, status=201)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def livraison_vendor(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            if data['confirm']:
                result = confirmer_livraison_vendor(data['transaction'])
                return JsonResponse(result, safe=False, status=201)
            elif data['confirm'] == False:
                result = annuler_livraison_vendor(data['transaction'])
                return JsonResponse(result, safe=False, status=201)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)
