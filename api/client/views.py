from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.http import JsonResponse, HttpResponse
from .actions import retrait, payement, achat_credit, fast_payement, participer_cagnote, cloturer_cagnote, update_participation_cagnote, payement_masse, supprimer_cagnote, paiement_somelec
from api.models import *
from users.models import ClientDigiPay, Vendor, MyUser, TransactionModel, Transfert, Transaction, PreTransaction, TransfertDirect, Client, Cagnote, ParticipantsCagnote, GroupPayement, BeneficiaresGrpPayement, Facturier, Notification
from users.serializers import PreTransactionFullSerializer, Vendor_UserSerializer, CagnoteFullSerializer, ParticipationCagnoteSerializer, BeneficiaresGrpPayementFullSerializer, CLientDigipay_ProfilSerializer, Grp_PayementFullSerializer
from api.serializers import TransfertFullSerializer
from users.serializers import PreTransactionFullSerializer, TransfertDirectFullSerializer
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
                user = ClientDigiPay.objects.get(id=data['id'])
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
            pre_transaction = PreTransaction.objects.filter(
                code_secret=data['code'], status=TransactionModel.TO_VALIDATE, type_transaction=PreTransaction.PAIEMENT)
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
                return JsonResponse({'msg': "Aucun commerçant n'est associé avec ce code !"}, safe=False, status=200)
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
            client = ClientDigiPay.objects.get(id=data['client'])
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
            client = ClientDigiPay.objects.get(id=data['client'])
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
            client = ClientDigiPay.objects.get(id=data['client'])
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
                client = ClientDigiPay.objects.get(id=data['client_origine'])
                result = client.envoyer(
                    data['client_destinataire'], data['montant'])
                return JsonResponse(result, safe=False, status=201)
            elif 'tel' in data.keys():
                client = ClientDigiPay.objects.get(id=data['client_origine'])
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
            pre_transaction = PreTransaction.objects.get(
                id=data['pre_transaction'])
            result = pre_transaction.client_retrait(
                data['agence_destination'], data['nom_destinataire'])
            return JsonResponse(result, safe=False, status=201)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)

# cagnotte


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
                    p = ParticipantsCagnote.objects.get(
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
def getParticipantsCagnote(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            cagnote = Cagnote.objects.get(id=data['cagnote'])
            result = ParticipationCagnoteSerializer(
                ParticipantsCagnote.objects.filter(cagnote=cagnote).order_by('-date'), many=True).data
            return JsonResponse(result, safe=False, status=200)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def check_clientDigiPay_newCagnote(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            client = list(ClientDigiPay.objects.filter(tel=data['tel']))
            if len(client) == 0:
                result = {
                    'msg': "Aucun client digiPay n'est associe a ce numero de telephone !  "}
                return JsonResponse(result, safe=False, status=200)

            client = client[0]
            if not client.is_active:
                result = {'msg': "ce client digiPay n'est plus active !  "}
                return JsonResponse(result, safe=False, status=200)

            result = CLientDigipay_ProfilSerializer(client).data
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
            client = ClientDigiPay.objects.get(id=data['client'])
            beneficiaire = ClientDigiPay.objects.get(
                id=data['beneficiaire'])
            cagnote = Cagnote(
                nom=data['nom'], objectif=data['objectif'], motif=data['motif'], responsable=client, beneficiaire=beneficiaire)
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
                if not result["actif"] or result["archive"] or result['verse_au_solde']:
                    return JsonResponse({'msg': " Cette cagnotte n'est plus actif ou archivé !"}, safe=False, status=200)
                elif result["responsable"]['id'] == user.id:
                    return JsonResponse({'msg': " Vous etes responsable de cette cagnotte , pour faire un don aller vers la liste des cagnottes !"}, safe=False, status=200)
                elif result["beneficiaire"]['id'] == user.id:
                    return JsonResponse({'msg': " Vous etes le beneficiaire de cette cagnotte !"}, safe=False, status=200)
                else:
                    participants = ParticipantsCagnote.objects.filter(
                        cagnote=cagnote[0], participant=user)
                    if len(list(participants)) != 0:
                        return JsonResponse({'msg': " Vous etes deja paticipant a cette cagnotte !"}, safe=False, status=200)
                    else:
                        return JsonResponse(result, safe=False, status=200)
            else:
                return JsonResponse({'msg': "Cet identifiant n'est pas associé a une cagnotte !"}, safe=False, status=200)
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
            client = ClientDigiPay.objects.get(id=data['client'])
            result = participer_cagnote(client, cagnote, data['montant'])
            return JsonResponse(result, safe=False, status=201)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def client_update_participation_cagnote(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            cagnote = Cagnote.objects.get(id=data['cagnote'])
            client = ClientDigiPay.objects.get(id=data['client'])
            result = update_participation_cagnote(
                client, cagnote, data['montant'])
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
            beneficiaire = ClientDigiPay.objects.get(
                id=cagnote.beneficiaire.id)
            result = cloturer_cagnote(beneficiaire, cagnote)
            return JsonResponse(result, safe=False, status=201)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def client_delete_cagnote(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            cagnote = Cagnote.objects.get(id=data['cagnote'])
            result = supprimer_cagnote(cagnote)
            return JsonResponse(result, safe=False, status=201)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)

# paiement de masse


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def getBeneficiares_grpPayement(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            grp_payement = GroupPayement.objects.get(id=data['grp_payement'])
            result = BeneficiaresGrpPayementFullSerializer(
                BeneficiaresGrpPayement.objects.filter(grp_payement=grp_payement).order_by('-date'), many=True).data
            return JsonResponse(result, safe=False, status=200)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def getBeneficiares_by_codeGrpPayement(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            user = MyUser.objects.get(id=data['user'])
            transferts = TransfertDirect.objects.filter(
                numero_grp_payement=data['numero_grp_payement'], expediteur=user).order_by('-date_creation')

            result = TransfertDirectFullSerializer(
                transferts, many=True).data

            return JsonResponse(result, safe=False, status=200)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def check_clientDigiPay_grpPayement(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            client = list(ClientDigiPay.objects.filter(tel=data['tel']))
            if len(client) == 0:
                result = {
                    'msg': "Aucun client digiPay n'est associe a ce numero de telephone !  "}
                return JsonResponse(result, safe=False, status=200)

            client = client[0]
            if not client.is_active:
                result = {'msg': "ce client digiPay n'est plus active !  "}
                return JsonResponse(result, safe=False, status=200)

            if client.id == data['user']:
                result = {
                    'msg': "ce numero de telephone est associe a votre compte !  "}
                return JsonResponse(result, safe=False, status=200)

            result = CLientDigipay_ProfilSerializer(client).data
            return JsonResponse(result, safe=False, status=200)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def client_add_beneficiaire_grpPayement(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            client = ClientDigiPay.objects.get(id=data['beneficiaire'])
            grp_payement = GroupPayement.objects.get(id=data['grp_payement'])

            existant_beneficiaire = BeneficiaresGrpPayement.objects.filter(
                beneficiaire=client, grp_payement=grp_payement)
            if(len(existant_beneficiaire) != 0):
                result = {
                    'msg': "ce client est deja existant dans ce groupe !  "}
                return JsonResponse(result, safe=False, status=200)

            beneficiaire = BeneficiaresGrpPayement(
                beneficiaire=client, grp_payement=grp_payement, montant=data['montant'], motif=data['motif'])
            beneficiaire.save()

            result = [BeneficiaresGrpPayementFullSerializer(
                beneficiaire).data, Grp_PayementFullSerializer(grp_payement).data]
            return JsonResponse(result, safe=False, status=200)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@api_view(['PUT'])
@permission_classes((IsAuthenticated,))
def client_update_beneficiaire_grpPayement(request, pk):
    if request.method == 'PUT':
        data = json.loads(request.body.decode('utf-8'))
        try:
            beneficiaire = BeneficiaresGrpPayement.objects.get(id=pk)
            beneficiaire.montant = data['montant']
            beneficiaire.motif = data['motif']
            beneficiaire.save()

            grp_payement = GroupPayement.objects.get(id=data['grp_payement'])

            result = [BeneficiaresGrpPayementFullSerializer(
                beneficiaire).data, Grp_PayementFullSerializer(grp_payement).data]

            return JsonResponse(result, safe=False, status=200)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def client_delete_beneficiaire_grpPayement(request, pk):
    if request.method == 'DELETE':
        try:
            beneficiaire = BeneficiaresGrpPayement.objects.get(id=pk)
            grp_payement = GroupPayement.objects.get(
                id=beneficiaire.grp_payement.id)

            result = [BeneficiaresGrpPayementFullSerializer(
                beneficiaire).data]

            beneficiaire.delete()

            result.append(Grp_PayementFullSerializer(grp_payement).data)
            return JsonResponse(result, safe=False, status=200)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def client_payement_masse(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            grp_payement = GroupPayement.objects.get(id=data['grp_payement'])
            grp_payement.motif = data['motif']
            grp_payement.save()

            beneficiaires = BeneficiaresGrpPayement.objects.filter(
                grp_payement=grp_payement)

            destinataires = []
            for b in beneficiaires:
                temp = {'user': ClientDigiPay.objects.get(
                    id=b.beneficiaire.id), 'montant': b.montant, 'motif': b.motif}
                destinataires.append(temp)

            entreprise = ClientDigiPay.objects.get(id=data['expediteur'])

            result = payement_masse(
                entreprise, destinataires, grp_payement.total_montant, grp_payement.motif)

            return JsonResponse(result, safe=False, status=200)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)

# somelec facture


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def client_somelec_payement(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            client = ClientDigiPay.objects.get(id=data['client'])
            facturier = Facturier.objects.get(id=data['facturier'])
            result = paiement_somelec(client, facturier, data)
            return JsonResponse(result, safe=False, status=200)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def client_somelec_reclamation(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            client = ClientDigiPay.objects.get(id=data['client'])
            facturier = Facturier.objects.get(id=data['facturier'])
            transaction = Transaction.objects.get(id=data['transaction'])
            transfert = TransfertDirect.objects.get(
                id=transaction.transaction.id)
            ####
            msgClient = Notification(
                user=client, transaction=transfert, status=Notification.PAIEMENT_FACTURE,
                message="Attention ! le paiement de votre facture N° " + transfert.libele + " de la transaction : " + transaction.code_transaction + " a été interompu. Veuillez aller vers une agence de la Somelec")
            msgClient.save()

            msgFacturier = Notification(
                user=facturier, transaction=transfert, status=Notification.PAIEMENT_FACTURE,
                message="Le paiement de la facture N° " + transfert.libele + " de la transaction : "+transaction.code_transaction + " a été interompu. Veuillez confirmer le paiement")
            msgFacturier.save()

            result = {'msg': 'Operation complete !'}
            return JsonResponse(result, safe=False, status=200)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)
