from users.models import TransactionModel, Transfert, Transaction, Client_DigiPay, MyUser, Vendor, Client, Pre_Transaction, Compensation, Notification
from api.models import Agence
from api.serializers import TransactionFullSerializer, TransfertFullSerializer


def transfert(agence_origine, data):
    agence_destination = Agence.objects.get(id=data['agence_destination'])

    if data['destinataireInfo']['digipay']:
        return {'msg': "L'envoie vers un compte un digipay n'est pas disponible pour le moment ..."}
    destinataire = Client.objects.get(id=data['destinataireInfo']['id'])

    expediteur = None
    if data['expediteurInfo']:
        # if data['expediteurInfo']['digipay']:
        #    return {'msg': "Nous vous conseillons d'utiliser l'application mobile digiPay !"}
        # else:
        if data['expediteurInfo']['id'] == data['destinataireInfo']['id']:
            return {'msg': "L'expéditeur doit être différent du destinataire !"}

        expediteur = data['expediteurInfo']['id']

    transfert = Transfert(agence_origine=agence_origine,
                          agence_destination=agence_destination,
                          destinataire=destinataire,
                          expediteur=expediteur,
                          categorie_transaction=data['categorie_transaction'],
                          status=TransactionModel.NOT_WITHDRAWED,
                          montant=data['montant'],
                          frais_origine=data['frais_origine'],
                          frais_destination=data['frais_destination'],
                          remarque=data['remarque'])
    transfert.save()
    ##
    transaction = Transaction(transaction=transfert, type_transaction=Transaction.TRANSFERT,
                              date=transfert.date_creation, categorie_transaction=transfert.categorie_transaction)
    transaction.save()

    agence_origine.frais += transfert.frais_origine
    agence_origine.solde += transfert.montant + transfert.frais_origine
    agence_origine.save()

    ##
    result = TransactionFullSerializer(transaction).data
    result['transaction'] = TransfertFullSerializer(transfert).data

    # print(' result ', result)
    return result

    # else:
    # return {'msg': "le solde de l'agence est insuffisant pour effectuer cette opération"}


def retrait(agence_destination, data):
    transfert = Transfert.objects.get(id=data['id'])
    if agence_destination.solde >= transfert.montant:
        transfert.status = TransactionModel.WITHDRAWED
        transfert.save()
        ##

        transaction = Transaction(transaction=transfert, type_transaction=Transaction.RETRAIT,
                                  date=transfert.date_modifcation, categorie_transaction=transfert.categorie_transaction)
        transaction.save()
        ##

        agence_destination.frais += transfert.frais_destination
        agence_destination.solde = agence_destination.solde - \
            transfert.montant + transfert.frais_destination
        agence_destination.retrait += transfert.montant
        agence_destination.save()

        ##
        result = TransactionFullSerializer(transaction).data
        result['transaction'] = TransfertFullSerializer(transfert).data

        # print(' result ', result)
        return result
    else:
        return {'msg': "le solde de l'agence est insuffisant pour effectuer cette opération"}


def recharge(agence, receiver, montant):
    # agence = Agence.objects.get(id=data['agence'])

    if receiver['role'] == MyUser.CLIENT:
        destinataire = Client_DigiPay.objects.get(id=receiver['id'])
    elif receiver['role'] == MyUser.VENDOR:
        destinataire = Vendor.objects.get(id=receiver['id'])
    else:
        return {'msg': "L'utilisateur de ce compte est inexistant"}

    categorie = Transfert.SUP_3000 if montant > 3000 else Transfert.INF_3000
    client_fictif = Client.objects.get(id=destinataire.client)
    transfert = Transfert(agence_origine=agence,
                          agence_destination=agence,
                          destinataire=client_fictif,
                          categorie_transaction=categorie,
                          status=TransactionModel.COMFIRMED,
                          montant=montant,
                          frais_origine=0,
                          frais_destination=0,)
    transfert.save()

    transaction = Transaction(transaction=transfert, type_transaction=Transaction.RECHARGE,
                              date=transfert.date_creation, categorie_transaction=transfert.categorie_transaction)
    transaction.save()

    destinataire.solde += montant
    destinataire.save()

    agence.solde += transfert.montant
    agence.save()

    result = TransactionFullSerializer(transaction).data
    result['transaction'] = TransfertFullSerializer(transfert).data

    '''
    T = Transaction.objects.create(
        sender=self,
        type="RECHARGE",
        receiver=destinataire,
        etat="VALIDE",
        montant=montant,
        num_transaction=int(time.time()))
    T.save()
    '''

    # conntentAgence = "Vous avez rechargé " + str(montant) + " pour le client dont numéro est : " + destinataire.user.username
    # conntentClient = "Vous avez rechargé votre compte d'un montant  de " + str(montant) + " MRU "

    # send_message(destinataire, self, conntentAgence, "RECHARGE")
    # send_message(self, destinataire, conntentClient, "RECHARGE")

    return result


def retrait_par_code(agence, pre_transactionId):
    # client et vendor
    pre_transaction = Pre_Transaction.objects.get(id=pre_transactionId)
    client = list(Client_DigiPay.objects.filter(
        id=pre_transaction.expediteur.id))
    vendor = list(Vendor.objects.filter(id=pre_transaction.expediteur.id))

    expediteur = None
    if len(client) != 0:
        expediteur = client[0]
    elif len(vendor) != 0:
        expediteur = vendor[0]
    else:
        return{'msg': "le numéro de téléphone n'est pas associé à un compte client ou commerçant !"}

    if agence.solde >= pre_transaction.montant:
        categorie = Transfert.SUP_3000 if pre_transaction.montant > 3000 else Transfert.INF_3000
        client_fictif = Client.objects.get(id=expediteur.client)
        ##
        transfert = Transfert(agence_destination=agence,
                              agence_origine=agence,
                              destinataire=client_fictif, montant=pre_transaction.montant, categorie_transaction=categorie,
                              status=TransactionModel.WITHDRAWED, code_secret=pre_transaction.code_secret)
        transfert.save()

        transaction = Transaction(transaction=transfert, type_transaction=Transaction.RETRAIT,
                                  date=transfert.date_creation, categorie_transaction=transfert.categorie_transaction)
        transaction.save()

        pre_transaction.status = TransactionModel.COMFIRMED
        pre_transaction.save()

        agence.solde -= pre_transaction.montant
        agence.retrait += pre_transaction.montant
        agence.save()

        expediteur.solde -= pre_transaction.montant
        expediteur.save()

        result = TransactionFullSerializer(transaction).data
        result['transaction'] = TransfertFullSerializer(transfert).data
        return result
    else:
        return {'msg': "le solde l'agence est insuffisant pour effectuer cette opération"}


def confirmer_compensation(agence, transactionID, notifID):
    compensation = Compensation.objects.get(id=transactionID)
    transaction = Transaction.objects.get(transaction=compensation)
    notification = Notification.objects.get(id=notifID)

    if transaction.type_transaction == Transaction.COMP_VERSEMENT:
        compensation.status = Compensation.COMFIRMED
        compensation.save()

        agence.solde += compensation.montant
        agence.save()

        notification.delete()
        return {'result': 'Compensation validée avec succes !'}
    elif transaction.type_transaction == Transaction.COMP_RETRAIT:
        if agence.solde >= compensation.montant:
            compensation.status = Compensation.COMFIRMED
            compensation.save()

            agence.solde -= compensation.montant
            agence.save()

            notification.delete()
            return {'result': 'Compensation validée avec succes !'}
        else:
            return {'msg': "le solde de l'agence est insuffisant pour effectuer cette opération"}


def annuler_compensation(agence, transactionID, notifID):
    ###
    compensation = Compensation.objects.get(id=transactionID)
    compensation.status = Compensation.CANCELED
    compensation.save()
    ##
    notification = Notification.objects.get(id=notifID)
    notification.delete()
    return {'result': 'Compensation annulée avec succes !'}
