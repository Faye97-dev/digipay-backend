from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from .models import HOST
from django.http import JsonResponse, HttpResponse
# from users.models import Transfert, Transaction, Client_DigiPay, Pre_Transaction
from users.models import *
from users.serializers import ClientDigiPay_UserSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
import json
from django.db.models import Sum, Q
# need to move this method in a file


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def check_clientDigiPay(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            sender = Client_DigiPay.objects.get(id=data['sender'])
            if str(sender.tel) == str(data['tel']):
                result = {
                    'msg': 'le numéro de téléphone du client est similaire au numéro du compte utilisateur !'}
                return JsonResponse(result, safe=False, status=200)

            soldeEnough = True if sender.solde > data['montant'] else False
            if not soldeEnough:
                result = {
                    'msg': 'Votre solde est insuffisant pour effectuer cette opération !'}
                return JsonResponse(result, safe=False, status=200)

            vendor = list(Vendor.objects.filter(tel=data['tel']))
            employe = list(Employee.objects.filter(tel=data['tel']))
            responsable = list(Responsable.objects.filter(tel=data['tel']))
            agent = list(Agent.objects.filter(tel=data['tel']))
            admin = list(SysAdmin.objects.filter(tel=data['tel']))

            if len(vendor) != 0 or len(employe) != 0 or len(responsable) != 0 or len(agent) != 0 or len(admin) != 0:
                result = {'msg': "Ce numéro de téléphone n'est pas autorisé !"}
                return JsonResponse(result, safe=False, status=200)

            client = list(Client_DigiPay.objects.filter(tel=data['tel']))
            if len(client) == 0:
                result = {'client': data['tel'],
                          'check': False, 'montant': data['montant']}
            else:
                result = {'client': ClientDigiPay_UserSerializer(
                    client[0]).data, 'check': True, 'montant': data['montant']}

            return JsonResponse(result, safe=False, status=200)
        except:
            return JsonResponse({'msg': ' Exception error !'}, safe=False, status=400)
    else:
        return HttpResponse(status=405)


def transactionListByUser(user):
    if user.role == MyUser.RESPONSABLE_AGENCE:
        user = Responsable.objects.get(id=user.id)
        transferts = [item.id for item in list(
            Transfert.objects.filter(agence_origine=user.agence))]
        ###
        retraits = [item.id for item in list(
            Transfert.objects.filter(agence_destination=user.agence))]
        ###
        # compensations = []  # implenter dans la views TransactionCompensationListAPIViews
        ###
        res = Transaction.objects.filter(
            transaction__id__in=list(set(transferts+retraits))).order_by('-date')
        print('transactions list RESPONSABLE_AGENCE  .....')
        return res

    elif user.role == MyUser.EMPLOYE_AGENCE:
        user = Employee.objects.get(id=user.id)
        transferts = [item.id for item in list(
            Transfert.objects.filter(agence_origine=user.agence))]
        ###
        retraits = [item.id for item in list(
            Transfert.objects.filter(agence_destination=user.agence))]
        ###
        res = Transaction.objects.filter(
            transaction__id__in=list(set(transferts+retraits))).order_by('-date')
        print('transactions list EMPLOYE_AGENCE  .....')
        return res

    elif user.role == MyUser.CLIENT:
        # handle some cases .... when expediteur is a digiPay client can do a transfert and retrait ??
        # block other type user vendor ,responsable , employee , agent de compensation
        user = Client_DigiPay.objects.get(id=user.id)
        client_fictif = Client.objects.get(id=user.client)
        ###
        retraits_agence = Transfert.objects.filter(expediteur=user.client)
        retraits_agence = [item.id for item in list(
            retraits_agence) if item.agence_destination == item.agence_origine]  # type_transaction est RETRAIT par sms client anonyme

        recharges_agence = Transfert.objects.filter(
            destinataire=client_fictif)
        recharges_agence = [item.id for item in list(
            recharges_agence) if item.agence_destination == item.agence_origine]  # type_transaction est RETRAIT ou RECHARGE

        # retraits_agence = [item.id for item in list(
        # Transfert.objects.filter(expediteur=user.client))]
        # transfert_agence = [item.id for item in list(
        #    Transfert.objects.filter(destinataire__id=user.client))]
        ###
        transferts = [item.id for item in list(Transfert_Direct.objects.filter(
            expediteur=user))]
        retraits = [item.id for item in list(Transfert_Direct.objects.filter(
            destinataire=user))]

        donations = [item.id for item in list(Transfert_Cagnote.objects.filter(
            expediteur=user.id))]
        recoltes = [item.id for item in list(Transfert_Cagnote.objects.filter(
            destinataire=user.id))]

        all_ = retraits_agence+recharges_agence+transferts+retraits+donations+recoltes
        res = Transaction.objects.filter(
            transaction__id__in=list(set(all_))).order_by('-date')
        print('transactions list CLIENT  .....')
        return res

    elif user.role == MyUser.VENDOR:
        user = Vendor.objects.get(id=user.id)
        client_fictif = Client.objects.get(id=user.client)

        recharges_agence = Transfert.objects.filter(
            destinataire=client_fictif)
        recharges_agence = [item.id for item in list(
            recharges_agence) if item.agence_destination == item.agence_origine]

        transferts = [item.id for item in list(Transfert_Direct.objects.filter(
            expediteur=user))]
        retraits = [item.id for item in list(Transfert_Direct.objects.filter(
            destinataire=user))]
        res = Transaction.objects.filter(
            transaction__id__in=list(set(recharges_agence+transferts+retraits))).order_by('-date')
        print('transactions list VENDOR  .....')
        return res

    elif user.role == MyUser.SYSADMIN:
        transferts_agences = [
            item.id for item in list(Transfert.objects.all())]
        # transferts = [item.id for item in list(Transfert_Direct.objects.all())]
        # pre-transactions ?
        res = Transaction.objects.filter(transaction__id__in=list(
            set(transferts_agences))).order_by('-date')
        print('transactions list SYSADMIN  .....')
        return res
    else:
        return []


def compensationsListByUser(user):
    if user.role == MyUser.RESPONSABLE_AGENCE:
        user = Responsable.objects.get(id=user.id)
        compensations = [item.id for item in list(
            Compensation.objects.filter(agence=user.agence))]
        ###
        res = Transaction.objects.filter(
            transaction__id__in=list(set(compensations))).order_by('-date')
        print('compensations list RESPONSABLE_AGENCE  .....')
        return res

    elif user.role == MyUser.AGENT_COMPENSATION:
        user = Agent.objects.get(id=user.id)
        compensations = [item.id for item in list(
            user.compensations.all())]
        res = Transaction.objects.filter(
            transaction__id__in=list(set(compensations))).order_by('-date')
        print('compensations list AGENT_COMPENSATION  .....')
        return res
    elif user.role == MyUser.SYSADMIN:
        compensations = [item.id for item in list(
            Compensation.objects.all())]
        res = Transaction.objects.filter(
            transaction__id__in=list(set(compensations))).order_by('-date')
        print('compensations list SYSADMIN  .....')
        return res
    else:
        return []


def participationCagnoteListByUser(user):
    if user.role == MyUser.CLIENT:
        res = Participants_Cagnote.objects.filter(
            participant=user)
        return res
    else:
        return []


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def profile_statistiques(request, pk):
    result = {}
    user = MyUser.objects.get(pk=pk)
    transations_list = transactionListByUser(user)
    # statistiques
    if user.role == MyUser.VENDOR:
        payements_stats = [item.transaction.id for item in transations_list.filter(
            type_transaction=Transaction.PAIEMENT)]

        payements_recus = Transfert_Direct.objects.filter(
            Q(id__in=payements_stats) & Q(destinataire=user) &
            (Q(status=Transfert_Direct.COMFIRMED) | Q(status=Transfert_Direct.WITHDRAWED))).aggregate(Sum('montant'))['montant__sum'] or 0

        payements_faits = Transfert_Direct.objects.filter(
            Q(id__in=payements_stats) & Q(expediteur=user) &
            (Q(status=Transfert_Direct.COMFIRMED) | Q(status=Transfert_Direct.WITHDRAWED))).aggregate(Sum('montant'))['montant__sum'] or 0
        ###
        remboursements_stats = [item.transaction.id for item in transations_list.filter(
            type_transaction=Transaction.REMBOURSEMENT)]

        remboursements_recus = Transfert_Direct.objects.filter(
            Q(id__in=remboursements_stats) & Q(destinataire=user) &
            (Q(status=Transfert_Direct.COMFIRMED) | Q(status=Transfert_Direct.WITHDRAWED))).aggregate(Sum('montant'))['montant__sum'] or 0

        remboursements_faits = Transfert_Direct.objects.filter(
            Q(id__in=remboursements_stats) & Q(expediteur=user) &
            (Q(status=Transfert_Direct.COMFIRMED) | Q(status=Transfert_Direct.WITHDRAWED))).aggregate(Sum('montant'))['montant__sum'] or 0
        ###
        recharges_stats = [item.transaction.id for item in transations_list.filter(
            type_transaction=Transaction.RECHARGE)]

        recharges = Transfert.objects.filter(
            Q(id__in=recharges_stats) &
            (Q(status=Transfert.COMFIRMED) | Q(status=Transfert.WITHDRAWED))).aggregate(Sum('montant'))['montant__sum'] or 0
        ###
        retraits_stats = [item.transaction.id for item in transations_list.filter(
            type_transaction=Transaction.RETRAIT)]

        retraits = Transfert.objects.filter(
            Q(id__in=retraits_stats) &
            (Q(status=Transfert.COMFIRMED) | Q(status=Transfert.WITHDRAWED))).aggregate(Sum('montant'))['montant__sum'] or 0

        # print(payements_recus, payements_faits,
        #      remboursements_recus, remboursements_faits, recharges, retraits)
        result = {'payements_recus': payements_recus, 'payements_faits': payements_faits,
                  'remboursements_recus': remboursements_recus, 'remboursements_faits': remboursements_faits,
                  'recharges': recharges, 'retraits': retraits}

    elif user.role == MyUser.CLIENT:
        user = Client_DigiPay.objects.get(id=user.id)
        client_fictif = Client.objects.get(id=user.client)

        payements_stats = [item.transaction.id for item in transations_list.filter(
            type_transaction=Transaction.PAIEMENT)]

        payements_faits = Transfert_Direct.objects.filter(
            Q(id__in=payements_stats) &
            (Q(status=Transfert_Direct.COMFIRMED) | Q(status=Transfert_Direct.WITHDRAWED))).aggregate(Sum('montant'))['montant__sum'] or 0

        ###
        remboursements_stats = [item.transaction.id for item in transations_list.filter(
            type_transaction=Transaction.REMBOURSEMENT)]
        remboursements_recus = Transfert_Direct.objects.filter(
            Q(id__in=remboursements_stats) &
            (Q(status=Transfert_Direct.COMFIRMED) | Q(status=Transfert_Direct.WITHDRAWED))).aggregate(Sum('montant'))['montant__sum'] or 0

        ###
        envoies_stats = [item.transaction.id for item in transations_list.filter(
            type_transaction=Transaction.ENVOI)]

        envoies_recus = Transfert_Direct.objects.filter(
            Q(id__in=envoies_stats) & Q(destinataire=user) &
            (Q(status=Transfert_Direct.COMFIRMED) | Q(status=Transfert_Direct.WITHDRAWED))).aggregate(Sum('montant'))['montant__sum'] or 0

        envoies_faits = Transfert_Direct.objects.filter(
            Q(id__in=envoies_stats) & Q(expediteur=user) &
            (Q(status=Transfert_Direct.COMFIRMED) | Q(status=Transfert_Direct.WITHDRAWED))).aggregate(Sum('montant'))['montant__sum'] or 0
        ###
        recharges_stats = [item.transaction.id for item in transations_list.filter(
            type_transaction=Transaction.RECHARGE)]

        recharges = Transfert.objects.filter(
            Q(id__in=recharges_stats) &
            (Q(status=Transfert.COMFIRMED) | Q(status=Transfert.WITHDRAWED))).aggregate(Sum('montant'))['montant__sum'] or 0
        ###
        retraits_stats = [item.transaction.id for item in transations_list.filter(
            type_transaction=Transaction.RETRAIT)]

        mes_retraits = Transfert.objects.filter(
            Q(id__in=retraits_stats) & Q(destinataire=client_fictif) &
            (Q(status=Transfert.COMFIRMED) | Q(status=Transfert.WITHDRAWED))).aggregate(Sum('montant'))['montant__sum'] or 0

        retraits_par_sms = Transfert.objects.filter(
            Q(id__in=retraits_stats) & Q(destinataire=client_fictif, _negated=True) &
            (Q(status=Transfert.COMFIRMED) | Q(status=Transfert.WITHDRAWED))).aggregate(Sum('montant'))['montant__sum'] or 0

        # print(payements_faits, remboursements_recus, envoies_recus,
        #      envoies_faits, recharges, mes_retraits, retraits_par_sms)

        result = {'payements': payements_faits, 'remboursements': remboursements_recus,
                  'envoies_recus': envoies_recus, 'envoies_faits': envoies_faits,
                  'recharges': recharges, 'retraits': mes_retraits, 'retraits_par_sms': retraits_par_sms}

    elif user.role == MyUser.EMPLOYE_AGENCE:
        retraits_stats = [item.transaction.id for item in transations_list.filter(
            type_transaction=Transaction.RETRAIT)]

        retraits = Transfert.objects.filter(
            Q(id__in=retraits_stats) &
            (Q(status=Transfert.COMFIRMED) | Q(status=Transfert.WITHDRAWED))).aggregate(Sum('montant'))['montant__sum'] or 0
        ###
        recharges_stats = [item.transaction.id for item in transations_list.filter(
            type_transaction=Transaction.RECHARGE)]

        recharges = Transfert.objects.filter(
            Q(id__in=recharges_stats) &
            (Q(status=Transfert.COMFIRMED) | Q(status=Transfert.WITHDRAWED))).aggregate(Sum('montant'))['montant__sum'] or 0
        ###
        transferts_stats = [item.transaction.id for item in transations_list.filter(
            type_transaction=Transaction.TRANSFERT)]

        transferts = Transfert.objects.filter(
            Q(id__in=transferts_stats) &
            (Q(status=Transfert.COMFIRMED) | Q(status=Transfert.WITHDRAWED))).aggregate(Sum('montant'))['montant__sum'] or 0

        result = {'recharges': recharges,
                  'retraits': retraits, 'transferts': transferts}

    elif user.role == MyUser.RESPONSABLE_AGENCE:
        retraits_stats = [item.transaction.id for item in transations_list.filter(
            type_transaction=Transaction.RETRAIT)]

        retraits = Transfert.objects.filter(
            Q(id__in=retraits_stats) &
            (Q(status=Transfert.COMFIRMED) | Q(status=Transfert.WITHDRAWED))).aggregate(Sum('montant'))['montant__sum'] or 0
        ###
        recharges_stats = [item.transaction.id for item in transations_list.filter(
            type_transaction=Transaction.RECHARGE)]

        recharges = Transfert.objects.filter(
            Q(id__in=recharges_stats) &
            (Q(status=Transfert.COMFIRMED) | Q(status=Transfert.WITHDRAWED))).aggregate(Sum('montant'))['montant__sum'] or 0
        ###
        transferts_stats = [item.transaction.id for item in transations_list.filter(
            type_transaction=Transaction.TRANSFERT)]

        transferts = Transfert.objects.filter(
            Q(id__in=transferts_stats) &
            (Q(status=Transfert.COMFIRMED) | Q(status=Transfert.WITHDRAWED))).aggregate(Sum('montant'))['montant__sum'] or 0

        # compensations
        compensations_list = compensationsListByUser(user)
        compensations_versement = [item.transaction.id for item in compensations_list.filter(
            type_transaction=Transaction.COMP_VERSEMENT)]

        compensations_versement = Compensation.objects.filter(
            Q(id__in=compensations_versement) &
            (Q(status=Transfert.COMFIRMED) | Q(status=Transfert.WITHDRAWED))).aggregate(Sum('montant'))['montant__sum'] or 0
        ###
        compensations_retraits = [item.transaction.id for item in compensations_list.filter(
            type_transaction=Transaction.COMP_RETRAIT)]

        compensations_retraits = Compensation.objects.filter(
            Q(id__in=compensations_retraits) &
            (Q(status=Transfert.COMFIRMED) | Q(status=Transfert.WITHDRAWED))).aggregate(Sum('montant'))['montant__sum'] or 0

        ###
        compensations_annules = [
            item.transaction.id for item in compensations_list]

        compensations_annules = Compensation.objects.filter(
            Q(id__in=compensations_annules) &
            (Q(status=Transfert.CANCELED))).aggregate(Sum('montant'))['montant__sum'] or 0
        ###
        compensations_en_attente = [
            item.transaction.id for item in compensations_list]

        compensations_en_attente = Compensation.objects.filter(
            Q(id__in=compensations_en_attente) &
            (Q(status=Transfert.TO_VALIDATE))).aggregate(Sum('montant'))['montant__sum'] or 0

        result = {'recharges': recharges, 'retraits': retraits,
                  'transferts': transferts, "compensations_versement": compensations_versement,
                  'compensations_retraits': compensations_retraits, 'compensations_annules': compensations_annules,
                  'compensations_en_attente': compensations_en_attente}

    elif user.role == MyUser.AGENT_COMPENSATION:
        compensations_list = compensationsListByUser(user)
        compensations_versement = [item.transaction.id for item in compensations_list.filter(
            type_transaction=Transaction.COMP_VERSEMENT)]

        compensations_versement = Compensation.objects.filter(
            Q(id__in=compensations_versement) &
            (Q(status=Transfert.COMFIRMED) | Q(status=Transfert.WITHDRAWED))).aggregate(Sum('montant'))['montant__sum'] or 0

        ###
        compensations_retraits = [item.transaction.id for item in compensations_list.filter(
            type_transaction=Transaction.COMP_RETRAIT)]

        compensations_retraits = Compensation.objects.filter(
            Q(id__in=compensations_retraits) &
            (Q(status=Transfert.COMFIRMED) | Q(status=Transfert.WITHDRAWED))).aggregate(Sum('montant'))['montant__sum'] or 0

        ###
        compensations_annules = [
            item.transaction.id for item in compensations_list]

        compensations_annules = Compensation.objects.filter(
            Q(id__in=compensations_annules) &
            (Q(status=Transfert.CANCELED))).aggregate(Sum('montant'))['montant__sum'] or 0
        ###
        compensations_en_attente = [
            item.transaction.id for item in compensations_list]

        compensations_en_attente = Compensation.objects.filter(
            Q(id__in=compensations_en_attente) &
            (Q(status=Transfert.TO_VALIDATE))).aggregate(Sum('montant'))['montant__sum'] or 0

        result = {"compensations_versement": compensations_versement,
                  'compensations_retraits': compensations_retraits,
                  'compensations_annules': compensations_annules,
                  'compensations_en_attente': compensations_en_attente}

    return JsonResponse(result, safe=False, status=200)
