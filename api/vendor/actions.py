from users.models import TransactionModel, Transfert, Transaction, ClientDigiPay, MyUser, Vendor, Client, PreTransaction, Notification, TransfertDirect
from api.models import Agence
from api.serializers import TransactionFullSerializer, TransfertFullSerializer, NotificationSerializer
from users.serializers import TransfertDirectFullSerializer
import uuid
#from datetime import timedelta, datetime
from api.utils import random_code


def code_payement(vendor, montant, livraison, libele, delai):
    codes_list = [item.code_secret for item in PreTransaction.objects.all()]
    code_confirmation = random_code(4, codes_list)

    if not livraison:
        pre_transaction = PreTransaction(
            expediteur=vendor,
            status=TransactionModel.TO_VALIDATE,
            type_transaction=PreTransaction.PAIEMENT,
            montant=montant,
            code_secret=code_confirmation,
            livraison=livraison,
            libele=libele,
        )
        pre_transaction.save()
    else:
        #delai = datetime.now() + timedelta(days=delai)
        pre_transaction = PreTransaction(
            expediteur=vendor,
            status=TransactionModel.TO_VALIDATE,
            type_transaction=PreTransaction.PAIEMENT,
            montant=montant,
            code_secret=code_confirmation,
            livraison=livraison,
            libele=libele,
            delai_livraison=delai
        )
        pre_transaction.save()

    # notifications
    msgSelf = Notification(
        user=vendor, transaction=pre_transaction, status=Notification.DEMANDE_PAIEMENT,
        message="Vous avez générer un paiement de " + str(montant) + " MRU avec le code de confirmation: "+pre_transaction.code_secret)
    msgSelf.save()

    result = NotificationSerializer(msgSelf).data

    return {'code_confirmation': pre_transaction.code_secret, 'notification': result}


def confirmer_livraison_client(transactionId):
    transaction = Transaction.objects.get(id=transactionId)
    transfert = TransfertDirect.objects.get(id=transaction.transaction.id)
    commercant = Vendor.objects.get(id=transfert.destinataire.id)
    client = ClientDigiPay.objects.get(id=transfert.expediteur.id)

    client.on_hold -= transfert.montant
    client.save()

    commercant.solde += transfert.montant
    commercant.save()

    transfert.status = Transfert.COMFIRMED
    transfert.save()

    result = TransactionFullSerializer(transaction).data
    result['transaction'] = TransfertDirectFullSerializer(
        transfert).data

    return result


def confirmer_livraison_vendor(transactionId):
    transaction = Transaction.objects.get(id=transactionId)
    transfert = TransfertDirect.objects.get(id=transaction.transaction.id)
    commercant = Vendor.objects.get(id=transfert.destinataire.id)
    commercant_client = Vendor.objects.get(id=transfert.expediteur.id)

    commercant_client.on_hold -= transfert.montant
    commercant_client.save()

    commercant.solde += transfert.montant
    commercant.save()

    transfert.status = Transfert.COMFIRMED
    transfert.save()

    result = TransactionFullSerializer(transaction).data
    result['transaction'] = TransfertDirectFullSerializer(
        transfert).data

    return result


def annuler_livraison_client(transactionId):
    transaction = Transaction.objects.get(id=transactionId)
    transfert = TransfertDirect.objects.get(id=transaction.transaction.id)
    client = ClientDigiPay.objects.get(id=transfert.expediteur.id)

    client.on_hold -= transfert.montant
    client.solde += transfert.montant
    client.save()

    transfert.status = Transfert.CANCELED
    transfert.save()

    result = TransactionFullSerializer(transaction).data
    result['transaction'] = TransfertDirectFullSerializer(
        transfert).data

    return result


def annuler_livraison_vendor(transactionId):
    transaction = Transaction.objects.get(id=transactionId)
    transfert = TransfertDirect.objects.get(id=transaction.transaction.id)
    commercant_client = Vendor.objects.get(id=transfert.expediteur.id)

    commercant_client.on_hold -= transfert.montant
    commercant_client.solde += transfert.montant
    commercant_client.save()

    transfert.status = Transfert.CANCELED
    transfert.save()

    result = TransactionFullSerializer(transaction).data
    result['transaction'] = TransfertDirectFullSerializer(
        transfert).data

    return result


def fast_payement(commercant_client, commercant, montant, libele):
    if commercant_client.solde >= montant:
        transfert = TransfertDirect(
            expediteur=commercant_client,
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
            user=commercant_client, transaction=transfert, status=Notification.PAIEMENT,
            message="Vous avez effectué un paiement de " + str(montant) + " MRU au commerçant " + commercant.name + ' (' + commercant.tel+')')
        msgClient.save()

        msgCommercant = Notification(
            user=commercant, transaction=transfert, status=Notification.PAIEMENT,
            message="Vous avez reçu un paiement de " + str(montant) + " MRU du commerçant " + commercant_client.name + ' (' + commercant_client.tel+')')
        msgCommercant.save()
        '''

        commercant_client.solde -= montant
        commercant_client.save()

        commercant.solde += montant
        commercant.save()

        return result
    else:
        return {'msg': "Votre solde est insuffisant pour effectuer cette opération"}


def payement(commercant_client, pre_transactionId):
    pre_transaction = PreTransaction.objects.get(id=pre_transactionId)
    commercant = Vendor.objects.get(id=pre_transaction.expediteur.id)

    if commercant_client.solde >= pre_transaction.montant:
        if not pre_transaction.livraison:
            transfert = TransfertDirect(
                expediteur=commercant_client,
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
                user=commercant_client, transaction=transfert, status=Notification.PAIEMENT,
                message="Vous avez effectué un paiement de " + str(pre_transaction.montant) + " MRU au commerçant " + commercant.name + ' (' + commercant.tel+') avec le code confirmation: '+pre_transaction.code_secret)
            msgClient.save()

            msgCommercant = Notification(
                user=commercant, transaction=transfert, status=Notification.PAIEMENT,
                message="Vous avez reçu un paiement de " + str(pre_transaction.montant) + " MRU du commerçant " + commercant_client.name + ' (' + commercant_client.tel+') avec le code confirmation: '+pre_transaction.code_secret)
            msgCommercant.save()
            '''

            commercant_client.solde -= pre_transaction.montant
            commercant_client.save()

            commercant.solde += pre_transaction.montant
            commercant.save()

            pre_transaction.delete()
            return result
        else:
            codes_list = [
                item.code_secret for item in PreTransaction.objects.all()]
            code_confirmation = random_code(4, codes_list)
            transfert = TransfertDirect(
                expediteur=commercant_client,
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

            msgClient = Notification(
                user=commercant_client, transaction=transfert, status=Notification.PAIEMENT,
                message="Vous avez effectué un paiement de " + str(pre_transaction.montant) + " MRU au commerçant " + commercant.name + ' (' + commercant.tel+'). Merci de fournir le code livraison '+transfert.code_secret)
            msgClient.save()

            msgCommercant = Notification(
                user=commercant, transaction=transfert, status=Notification.PAIEMENT,
                message="Vous avez reçu un paiement de " + str(pre_transaction.montant) + " MRU du commerçant " + commercant_client.name + ' (' + commercant_client.tel+') . Merci de confirmer la livraison')
            msgCommercant.save()

            commercant_client.on_hold += pre_transaction.montant
            commercant_client.solde -= pre_transaction.montant
            commercant_client.save()

            pre_transaction.delete()
            return result
    else:
        return {'msg': "Votre solde est insuffisant pour effectuer cette opération"}


def remboursement(vendor, transactionId):
    prev_transaction = Transaction.objects.get(id=transactionId)
    prev_transfert = TransfertDirect.objects.get(
        id=prev_transaction.transaction.id)
    ###
    list_client = list(ClientDigiPay.objects.filter(
        id=prev_transfert.expediteur.id))
    list_vendor = list(Vendor.objects.filter(id=prev_transfert.expediteur.id))
    if len(list_client) != 0:
        receiver = list_client[0]
    elif len(list_vendor) != 0:
        receiver = list_vendor[0]
    else:
        return {'msg': "Type d'utilisateur invalid !"}

    if vendor.solde >= prev_transfert.montant:
        transfert = TransfertDirect(
            expediteur=vendor,
            destinataire=receiver,
            status=TransactionModel.COMFIRMED,
            montant=prev_transfert.montant)
        transfert.save()

        transaction = Transaction(
            transaction=transfert, type_transaction=Transaction.REMBOURSEMENT, date=transfert.date_creation)
        transaction.save()

        result = TransactionFullSerializer(transaction).data
        result['transaction'] = TransfertDirectFullSerializer(
            transfert).data

        vendor.solde -= transfert.montant
        vendor.save()

        receiver.solde += transfert.montant
        receiver.save()

        prev_transfert.status = TransactionModel.CANCELED
        prev_transfert.save()

        prevTransaction_afterUpdate = TransactionFullSerializer(
            prev_transaction).data
        prevTransaction_afterUpdate['transaction'] = TransfertDirectFullSerializer(
            prev_transfert).data
        return [result, prevTransaction_afterUpdate]
    else:
        return {'msg': "Votre solde est insuffisant pour effectuer cette opération"}
