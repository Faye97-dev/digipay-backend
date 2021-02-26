from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from .models import HOST
from django.http import JsonResponse, HttpResponse
import requests
from users.models import Transfert, Transaction, Client_DigiPay, Pre_Transaction, Transfert_Direct
from .models import *
from .serializers import TransfertFullSerializer
from users.serializers import PreTransactionFullSerializer
import json


def send_request(url, data, method, headers=None):
    if method == 'POST':
        response = requests.post(url, data=data)
    elif method == 'PUT':
        response = requests.put(url, data=data)
    elif method == 'GET':
        response = requests.get(url)
    elif method == 'DELETE':
        response = requests.delete(url)
        return [{}, response.status_code]

    result = response.json()
    return [result, response.status_code]


@csrf_exempt
def check_secret_key(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            result = {'checked': False}
            if data['model_transaction'] == 'TRANSFERT':
                transaction = Transfert.objects.get(id=data['id'])
            elif data['model_transaction'] == 'TRANSFERT_DIRECT':
                transaction = Transfert_Direct.objects.get(id=data['id'])
            elif data['model_transaction'] == 'PRE_TRANSACTION':
                transaction = Pre_Transaction.objects.get(id=data['id'])
            else:
                return JsonResponse({'msg': ' Invalid Json format !'}, safe=False, status=400)

            if transaction.code_secret == data['secret_key']:
                result = {'checked': True}
            return JsonResponse(result, safe=False, status=200)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@csrf_exempt
def transactions_a_retirer(request):
    # sort data by  - date
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
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


@csrf_exempt
def add_transfert_atomic(request):
    form = request.POST['data']
    data = json.loads(form)
    data['status'] = 'NOT_WITHDRAWED'
    new_transfert = Transfert.add_transfert(data)
    print(new_transfert)


@csrf_exempt
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


@csrf_exempt
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


@csrf_exempt
def add_transfert(request):
    # headers = {
    #     'X-CSRFToken': csrf.get_token(request)
    # }

    # headers={'Authorization': 'access_token myToken'}

    if request.method == 'POST':

        #form = request.POST['data']
        #data = json.loads(form)
        data = json.loads(request.body.decode('utf-8'))
        # if data['type_transaction'] == Transfert.INF_3000:
        data['status'] = 'NOT_WITHDRAWED'

        add_transfert = send_request(
            HOST + 'api/transfert/create/', data, 'POST')
        if add_transfert[1] == 201:
            data = {
                "categorie_transaction": add_transfert[0]['categorie_transaction'],
                "type_transaction": Transaction.TRANSFERT,
                "date": add_transfert[0]['date_creation'],
                # "agence": add_transfert[0]['agence_origine'],
                "transaction": add_transfert[0]['id']
            }
            add_transaction = send_request(
                HOST + 'api/transaction/create/', data, 'POST')

            if add_transaction[1] == 201:
                id_ = str(add_transfert[0]['agence_origine'])
                data = send_request(
                    HOST + 'api/agence/get/'+id_+'/', None, 'GET')
                data = data[0]
                ##
                data['frais'] = data['frais'] + \
                    add_transfert[0]['frais_origine']
                data['solde'] = data['solde'] + add_transfert[0]['montant'] + \
                    add_transfert[0]['frais_origine']
                data['commune'] = data['commune']['commune_code']
                # dette , frais destination ?

                update_agence = send_request(
                    HOST + 'api/agence/update/'+id_+'/', data, 'PUT')

                if update_agence[1] == 200:
                    status = update_agence[1]
                    #result = {}
                    #result['transfert'] = add_transfert[0]
                    # result['transaction'] =

                    result = send_request(
                        HOST + 'api/transaction/get/'+str(add_transaction[0]['id'])+'/', None, 'GET')[0]
                    #print('done ....', result)
                    return JsonResponse(result, safe=False, status=status)

                    #result['agence'] = update_agence[0]
                else:
                    status = update_agence[1]
                    result = {}
                    result['transfert'] = add_transfert[0]
                    result['transaction'] = add_transaction[0]
                    result['agence'] = False

                return JsonResponse(result, safe=False, status=status)
            else:
                status = add_transaction[1]
                result = {}
                result['transfert'] = add_transfert[0]
                result['transaction'] = False
                result['agence'] = False
                return JsonResponse(result, safe=False, status=status)
        else:
            status = add_transfert[1]
            result = {}
            result['transfert'] = False
            result['transaction'] = False
            result['agence'] = False
            return JsonResponse(result, safe=False, status=status)
    else:
        return HttpResponse(status=405)


def error_transfert(request):
    if request.method == 'POST':
        form = request.POST['data']
        data = json.loads(form)
        id_ = str(data['id'])
        delete_transfert = send_request(
            HOST + 'api/transfert/delete/'+id_+'/', None, 'DELETE')

        if delete_transfert[1] == 204:
            status = 200
            result = {}
            result['transfert'] = True
        else:
            status = delete_transfert[1]
            result = {}
            result['transfert'] = False
        return JsonResponse(result, safe=False, status=status)
    else:
        return HttpResponse(status=405)


@csrf_exempt
def add_retrait(request):
    if request.method == 'POST':
        #form = request.POST['data']
        #data = json.loads(form)
        data = json.loads(request.body.decode('utf-8'))
        id_ = str(data['id'])

        data = send_request(HOST + 'api/transfert/get/'+id_+'/', None, 'GET')

        if data[1] == 200:
            data = data[0]
            data['agence_destination'] = data['agence_destination']['id']
            data['agence_origine'] = data['agence_origine']['id']
            data['destinataire'] = data['destinataire']['id']
            data['status'] = 'WITHDRAWED'
        else:
            data = data[0]

        add_retrait = send_request(
            HOST + 'api/transfert/update/'+id_+'/', data, 'PUT')

        if add_retrait[1] == 200:
            data = {
                "categorie_transaction": add_retrait[0]['categorie_transaction'],
                "type_transaction": Transaction.RETRAIT,
                "date": add_retrait[0]['date_modifcation'],
                # "agence": add_retrait[0]['agence_destination'],
                "transaction": add_retrait[0]['id']
            }
            add_transaction = send_request(
                HOST + 'api/transaction/create/', data, 'POST')

            if add_transaction[1] == 201:
                id_ = str(add_retrait[0]['agence_destination'])
                data = send_request(
                    HOST + 'api/agence/get/'+id_+'/', None, 'GET')
                data = data[0]
                ##
                data['frais'] = data['frais'] + \
                    add_retrait[0]['frais_destination']
                data['solde'] = data['solde'] - add_retrait[0]['montant'] + \
                    add_retrait[0]['frais_destination']
                data['retrait'] = data['retrait'] + add_retrait[0]['montant']

                data['commune'] = data['commune']['commune_code']
                # dette , frais destination ?

                update_agence = send_request(
                    HOST + 'api/agence/update/'+id_+'/', data, 'PUT')

                if update_agence[1] == 200:
                    status = update_agence[1]
                    #result = {}
                    #result['transfert'] = add_retrait[0]
                    # result['transaction']
                    result = send_request(
                        HOST + 'api/transaction/get/'+str(add_transaction[0]['id'])+'/', None, 'GET')[0]
                    return JsonResponse(result, safe=False, status=status)
                    #result['agence'] = update_agence[0]
                else:
                    status = update_agence[1]
                    result = {}
                    result['transfert'] = add_retrait[0]
                    result['transaction'] = add_transaction[0]
                    result['agence'] = False

                return JsonResponse(result, safe=False, status=status)
            else:
                status = add_transaction[1]
                result = {}
                result['transfert'] = add_retrait[0]
                result['transaction'] = False
                result['agence'] = False
                return JsonResponse(result, safe=False, status=status)
        else:
            status = add_retrait[1]
            result = {}
            result['transfert'] = False
            result['transaction'] = False
            result['agence'] = False
            return JsonResponse(result, safe=False, status=status)
    else:
        return HttpResponse(status=405)
