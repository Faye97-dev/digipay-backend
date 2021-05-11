from users.models import TransactionModel, Transfert, Transaction, Client_DigiPay, MyUser, Vendor, Client, Pre_Transaction, Notification, Transfert_Direct
from users.models import Participants_Cagnote, Cagnote, Transfert_Cagnote
from api.models import Agence
from api.serializers import TransactionFullSerializer, TransfertFullSerializer
from users.serializers import TransfertDirectFullSerializer, CagnoteFullSerializer
from api.utils import random_with_N_digits, random_code
import uuid
from random import randint


def retrait(sender, montant):
    if sender.solde >= montant:
        ##
        codes_list = [
            item.code_secret for item in Pre_Transaction.objects.all()]
        code_confirmation = random_code(4, codes_list)

        pre_transaction = Pre_Transaction(
            expediteur=sender,
            destinataire=sender.tel,
            status=TransactionModel.TO_VALIDATE,
            type_transaction=Pre_Transaction.RETRAIT,
            montant=montant,
            code_secret=code_confirmation)
        pre_transaction.save()

        # notifications
        msgSelf = Notification(
            user=sender, transaction=pre_transaction, status=Notification.DEMANDE_RETRAIT,
            message="Vous avez fait une demande de retrait de " + str(montant) + " MRU avec le code confirmation: "+pre_transaction.code_secret)
        msgSelf.save()

        # sender.solde -= montant
        # sender.save()
        return {'code_confirmation': "Opération réussie !"}
    else:
        return {'msg': "Votre solde est insuffisant pour effectuer cette opération"}


def fast_payement(client, commercant, montant, libele):
    if client.solde >= montant:
        transfert = Transfert_Direct(
            expediteur=client,
            destinataire=commercant,
            status=TransactionModel.COMFIRMED,
            montant=montant,
            libele=libele)
        transfert.save()

        transaction = Transaction(
            transaction=transfert, type_transaction=Transaction.PAIEMENT, date=transfert.date_creation)
        transaction.save()

        result = TransactionFullSerializer(transaction).data
        result['transaction'] = TransfertDirectFullSerializer(
            transfert).data

        '''
        msgClient = Notification(
            user=client, transaction=transfert, status=Notification.PAIEMENT,
            message="Vous avez effectué un paiement de " + str(montant) + " MRU au commerçant " + commercant.name + ' (' + commercant.tel+')')
        msgClient.save()

        msgCommercant = Notification(
            user=commercant, transaction=transfert, status=Notification.PAIEMENT,
            message="Vous avez reçu un paiement de " + str(montant) + " MRU du client " + client.name + ' (' + client.tel+')')
        msgCommercant.save()
        '''

        client.solde -= montant
        client.save()

        commercant.solde += montant
        commercant.save()

        return result
    else:
        return {'msg': "Votre solde est insuffisant pour effectuer cette opération"}


def payement(client, pre_transactionId):
    pre_transaction = Pre_Transaction.objects.get(id=pre_transactionId)
    commercant = Vendor.objects.get(id=pre_transaction.expediteur.id)

    if client.solde >= pre_transaction.montant:
        if not pre_transaction.livraison:
            transfert = Transfert_Direct(
                expediteur=client,
                destinataire=commercant,
                status=TransactionModel.COMFIRMED,
                montant=pre_transaction.montant,
                libele=pre_transaction.libele,
                livraison=pre_transaction.livraison)
            transfert.save()

            transaction = Transaction(
                transaction=transfert, type_transaction=Transaction.PAIEMENT, date=transfert.date_creation)
            transaction.save()

            result = TransactionFullSerializer(transaction).data
            result['transaction'] = TransfertDirectFullSerializer(
                transfert).data

            # notifications
            '''
            msgClient = Notification(
                user=client, transaction=transfert, status=Notification.PAIEMENT,
                message="Vous avez effectué un paiement de " + str(pre_transaction.montant) + " MRU au commerçant " + commercant.name + ' (' + commercant.tel+') avec le code confirmation: '+pre_transaction.code_secret)
            msgClient.save()

            msgCommercant = Notification(
                user=commercant, transaction=transfert, status=Notification.PAIEMENT,
                message="Vous avez reçu un paiement de " + str(pre_transaction.montant) + " MRU du client " + client.name + ' (' + client.tel+') avec le code confirmation: '+pre_transaction.code_secret)
            msgCommercant.save()
            '''

            client.solde -= pre_transaction.montant
            client.save()

            commercant.solde += pre_transaction.montant
            commercant.save()

            pre_transaction.delete()
            return result
        else:
            codes_list = [
                item.code_secret for item in Pre_Transaction.objects.all()]
            code_confirmation = random_code(4, codes_list)
            transfert = Transfert_Direct(
                expediteur=client,
                destinataire=commercant,
                status=TransactionModel.TO_VALIDATE,
                montant=pre_transaction.montant,
                libele=pre_transaction.libele,
                delai_livraison=pre_transaction.delai_livraison,
                livraison=pre_transaction.livraison,
                code_secret=code_confirmation)
            transfert.save()

            transaction = Transaction(
                transaction=transfert, type_transaction=Transaction.PAIEMENT, date=transfert.date_creation)
            transaction.save()

            result = TransactionFullSerializer(transaction).data
            result['transaction'] = TransfertDirectFullSerializer(
                transfert).data

            # notifications
            '''
            msgClient = Notification(
                user=client, transaction=transfert, status=Notification.PAIEMENT,
                message="Vous avez effectué un paiement de " + str(pre_transaction.montant) + " MRU au commerçant " + commercant.name + ' (' + commercant.tel+'). Merci de fournir le code livraison '+transfert.code_secret)
            msgClient.save()

            msgCommercant = Notification(
                user=commercant, transaction=transfert, status=Notification.PAIEMENT,
                message="Vous avez reçu un paiement de " + str(pre_transaction.montant) + " MRU du client " + client.name + ' (' + client.tel+') . Merci de confirmer la livraison')
            msgCommercant.save()
            '''

            client.on_hold += pre_transaction.montant
            client.solde -= pre_transaction.montant
            client.save()

            pre_transaction.delete()
            return result
    else:
        return {'msg': "Votre solde est insuffisant pour effectuer cette opération"}


def payement_masse(entreprise, clients, total, motif):
    if entreprise.solde >= total:
        numero_grp_payement = str(uuid.uuid4().hex.upper())
        for client in clients:
            transfert = Transfert_Direct(
                expediteur=entreprise,
                destinataire=client['user'],
                status=TransactionModel.COMFIRMED,
                montant=client["montant"],
                numero_grp_payement=numero_grp_payement,
                remarque=motif+" - "+client['motif'])
            transfert.save()

            transaction = Transaction(
                transaction=transfert, type_transaction=Transaction.PAIEMENT_MASSE, date=transfert.date_creation)
            transaction.save()

            client['user'].solde += transfert.montant
            client['user'].save()

            entreprise.solde -= transfert.montant
            entreprise.save()

        return {'transaction': "Opération réussie !"}
    else:
        return {'msg': "Votre solde est insuffisant pour effectuer cette opération"}


def achat_credit(client, numero, montant):
    # digipay commercant credit recharge
    commercant = list(Vendor.objects.filter(tel='11223344'))
    if len(commercant) == 0:
        return {'msg': "Aucun fournisseur de carte credit n'est disponible !"}
    else:
        commercant = commercant[0]

    operateur = str(numero)[0]
    if client.solde >= montant:
        carte = operateur + str(random_with_N_digits(13))

        transfert = Transfert_Direct(
            expediteur=client,
            destinataire=commercant,
            status=TransactionModel.COMFIRMED,
            montant=montant)
        transfert.save()

        transaction = Transaction(
            transaction=transfert, type_transaction=Transaction.PAIEMENT, date=transfert.date_creation)
        transaction.save()

        result = TransactionFullSerializer(transaction).data
        result['transaction'] = TransfertDirectFullSerializer(
            transfert).data

        # notifications

        msgClient = Notification(
            user=client, transaction=transfert, status=Notification.PAIEMENT,
            message="Vous avez acheté une carte de credit de " + str(montant) + " MRU , le code de recharge est : " + carte)
        msgClient.save()

        '''
        msgCommercant = Notification(
            user=commercant, transaction=transfert, status=Notification.PAIEMENT,
            message="Vous avez reçu un achat de credit de " + str(montant) + " MRU du client " + client.name + ' (' + client.tel+')')
        msgCommercant.save()
        '''

        client.solde -= montant
        client.save()

        commercant.solde += montant
        commercant.save()
        return result
    else:
        return {'msg': "Votre solde est insuffisant pour effectuer cette opération"}


def participer_cagnote(client, cagnote, montant):
    if client.solde >= montant:
        participation = Participants_Cagnote(
            participant=client, cagnote=cagnote, montant=montant)
        participation.save()

        transfert = Transfert_Cagnote(
            expediteur=client.id,
            destinataire=cagnote.id,
            type_transaction=Transfert_Cagnote.CAGNOTE,
            status=TransactionModel.COMFIRMED,
            montant=montant,
        )
        transfert.save()

        transaction = Transaction(
            transaction=transfert, type_transaction=Transaction.CAGNOTE, date=transfert.date_creation)
        transaction.save()

        client.solde -= montant
        client.save()

        cagnote.solde += montant
        cagnote.save()

        result = {}
        result['cagnote'] = CagnoteFullSerializer(cagnote).data
        result['participation'] = {
            'montant': participation.montant, 'date': participation.date.strftime('%d-%m-%Y %H:%M:%S')}

        return result
    else:
        return {'msg': "Votre solde est insuffisant pour effectuer cette opération"}


def update_participation_cagnote(client, cagnote, montant):
    if client.solde >= montant:
        participation = Participants_Cagnote.objects.filter(
            participant=client, cagnote=cagnote)
        transfert = Transfert_Cagnote.objects.filter(
            expediteur=client.id, destinataire=cagnote.id)

        if len(participation) == 0 or len(transfert) == 0:
            return {'msg': "Pas de participation fait par ce compte utilisateur !"}
        participation = participation[0]
        transfert = transfert[0]

        client.solde += participation.montant
        client.solde -= montant
        client.save()

        cagnote.solde -= participation.montant
        cagnote.solde += montant
        cagnote.save()

        transfert.montant = montant
        transfert.save()

        participation.montant = montant
        participation.save()

        result = {}
        result['cagnote'] = CagnoteFullSerializer(cagnote).data
        result['participation'] = {
            'montant': participation.montant, 'date': participation.date.strftime('%d-%m-%Y %H:%M:%S')}

        return result
    else:
        return {'msg': "Votre solde est insuffisant pour effectuer cette opération"}


def cloturer_cagnote(beneficiaire, cagnote):
    transfert = Transfert_Cagnote(
        expediteur=cagnote.id,
        destinataire=beneficiaire.id,
        type_transaction=Transfert_Cagnote.RECOLTE,
        status=TransactionModel.COMFIRMED,
        montant=cagnote.solde,
    )
    transfert.save()

    transaction = Transaction(
        transaction=transfert, type_transaction=Transaction.RECOLTE, date=transfert.date_creation)
    transaction.save()

    beneficiaire.solde += transfert.montant
    beneficiaire.save()

    cagnote.actif = False
    cagnote.verse_au_solde = True
    cagnote.save()

    temp = Client_DigiPay.objects.get(id=cagnote.responsable.id)
    msgClient = Notification(
        user=beneficiaire, transaction=transfert, status=Notification.CAGNOTE,
        message="Vous avez reçu une recolte de cagnotte de " + str(transfert.montant) + " MRU créer par " + temp.name + ' (' + temp.tel+')')
    msgClient.save()

    result = {}
    result['cagnote'] = CagnoteFullSerializer(cagnote).data
    participation = Participants_Cagnote.objects.filter(
        participant=cagnote.responsable, cagnote=cagnote)

    if len(list(participation)) != 0:
        result['participation'] = {
            'montant': participation[0].montant, 'date': participation[0].date.strftime('%d-%m-%Y %H:%M:%S')}
    else:
        result['participation'] = None

    return result
