from users.models import TransactionModel, Transfert, Transaction, Client_DigiPay, MyUser, Vendor, Client, Pre_Transaction, Notification, Transfert_Direct
from api.models import Agence
from api.serializers import TransactionFullSerializer, TransfertFullSerializer, NotificationSerializer
from users.serializers import TransfertDirectFullSerializer
import uuid
from datetime import timedelta, datetime


def code_payement(vendor, montant, livraison, libele, delai):
    code_confirmation = str(uuid.uuid4().hex[:8].upper())
    if not livraison:
        pre_transaction = Pre_Transaction(
            expediteur=vendor,
            status=TransactionModel.TO_VALIDATE,
            type_transaction=Pre_Transaction.PAIEMENT,
            montant=montant,
            code_secret=code_confirmation,
            livraison=livraison,
            libele=libele,
        )
        pre_transaction.save()
    else:
        #delai = datetime.now() + timedelta(days=delai)
        pre_transaction = Pre_Transaction(
            expediteur=vendor,
            status=TransactionModel.TO_VALIDATE,
            type_transaction=Pre_Transaction.PAIEMENT,
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
    transfert = Transfert_Direct.objects.get(id=transaction.transaction.id)
    commercant = Vendor.objects.get(id=transfert.destinataire.id)
    client = Client_DigiPay.objects.get(id=transfert.expediteur.id)

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


def annuler_livraison_client(transactionId):
    transaction = Transaction.objects.get(id=transactionId)
    transfert = Transfert_Direct.objects.get(id=transaction.transaction.id)
    client = Client_DigiPay.objects.get(id=transfert.expediteur.id)

    client.on_hold -= transfert.montant
    client.solde += transfert.montant
    client.save()

    transfert.status = Transfert.CANCELED
    transfert.save()

    result = TransactionFullSerializer(transaction).data
    result['transaction'] = TransfertDirectFullSerializer(
        transfert).data

    return result


def payement(commercant_client, pre_transactionId):
    pre_transaction = Pre_Transaction.objects.get(id=pre_transactionId)
    commercant = Vendor.objects.get(id=pre_transaction.expediteur.id)

    if commercant_client.solde >= pre_transaction.montant:
        transfert = Transfert_Direct(
            expediteur=commercant_client,
            destinataire=commercant,
            status=TransactionModel.COMFIRMED,
            montant=pre_transaction.montant)
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
            message="Vous avez effectué un paiement de " + str(pre_transaction.montant) + " MRU au commerçant " + commercant.name + ' (' + commercant.tel+') avec le code confirmation: '+pre_transaction.code_secret)
        msgClient.save()

        msgCommercant = Notification(
            user=commercant, transaction=transfert, status=Notification.PAIEMENT,
            message="Vous avez reçu un paiement de " + str(pre_transaction.montant) + " MRU du client " + commercant_client.name + ' (' + commercant_client.tel+') avec le code confirmation: '+pre_transaction.code_secret)
        msgCommercant.save()

        commercant_client.solde -= pre_transaction.montant
        commercant_client.save()

        commercant.solde += pre_transaction.montant
        commercant.save()

        #pre_transaction.status = TransactionModel.COMFIRMED
        # pre_transaction.save()
        pre_transaction.delete()

        return result
    else:
        return {'msg': "Votre solde est insuffisant pour effectuer cette opération"}


def remboursement(vendor, transactionId):
    prev_transaction = Transaction.objects.get(id=transactionId)
    prev_transfert = Transfert_Direct.objects.get(
        id=prev_transaction.transaction.id)
    ###
    list_client = list(Client_DigiPay.objects.filter(
        id=prev_transfert.expediteur.id))
    list_vendor = list(Vendor.objects.filter(id=prev_transfert.expediteur.id))
    if len(list_client) != 0:
        receiver = list_client[0]
    elif len(list_vendor) != 0:
        receiver = list_vendor[0]
    else:
        return {'msg': "Type d'utilisateur invalid !"}

    if vendor.solde >= prev_transfert.montant:
        transfert = Transfert_Direct(
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
