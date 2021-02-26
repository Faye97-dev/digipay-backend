from users.models import TransactionModel, Transfert, Transaction, Client_DigiPay, MyUser, Vendor, Client, Pre_Transaction, Notification, Transfert_Direct
from api.models import Agence
from api.serializers import TransactionFullSerializer, TransfertFullSerializer
from users.serializers import TransfertDirectFullSerializer
import uuid


def retrait(sender, montant):
    if sender.solde >= montant:
        ##
        code_confirmation = str(uuid.uuid4().hex[:8].upper())
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

        #sender.solde -= montant
        # sender.save()
        return {'code_confirmation': "Opération réussie !"}
    else:
        return {'msg': "Votre solde est insuffisant pour effectuer cette opération"}


def payement(client, pre_transactionId):
    pre_transaction = Pre_Transaction.objects.get(id=pre_transactionId)
    commercant = Vendor.objects.get(id=pre_transaction.expediteur.id)

    if client.solde >= pre_transaction.montant:
        transfert = Transfert_Direct(
            expediteur=client,
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
            user=client, transaction=transfert, status=Notification.PAIEMENT,
            message="Vous avez effectué un paiement de " + str(pre_transaction.montant) + " MRU au commerçant " + commercant.name + ' (' + commercant.tel+') avec le code confirmation: '+pre_transaction.code_secret)
        msgClient.save()

        msgCommercant = Notification(
            user=commercant, transaction=transfert, status=Notification.PAIEMENT,
            message="Vous avez reçu un paiement de " + str(pre_transaction.montant) + " MRU du client " + client.name + ' (' + client.tel+') avec le code confirmation: '+pre_transaction.code_secret)
        msgCommercant.save()

        client.solde -= pre_transaction.montant
        client.save()

        commercant.solde += pre_transaction.montant
        commercant.save()

        pre_transaction.status = TransactionModel.COMFIRMED
        pre_transaction.save()

        return result
    else:
        return {'msg': "Votre solde est insuffisant pour effectuer cette opération"}
