from users.models import TransactionModel, Transfert, Transaction, Client
from api.models import Agence
from api.serializers import TransactionFullSerializer, TransfertFullSerializer


def transfert(agence_origine, data):
    agence_destination = Agence.objects.get(id=data['agence_destination'])
    # if agence_origine.solde >= data['montant']:
    expediteur = data['expediteur'] if 'expediteur' in list(
        data.keys()) else None
    destinataire = Client.objects.get(id=data['destinataire'])
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

    #print(' result ', result)
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

        #print(' result ', result)
        return result
    else:
        return {'msg': "le solde de l'agence est insuffisant pour effectuer cette opération"}


'''
Transfert(agence_origine=data['agence_origine'],
            agence_destination=data['agence_destination'],
            destinataire=data['destinataire'],
            categorie_transaction=data['categorie_transaction'],
            status=data['status'],
            solde=data['solde'],
            frais_origine=data['frais_origine'],
            frais_destination=data['frais_destination'],
            remarque=data['remarque'],
            note=data['note'])
###
if expediteur.solde >= agence_destination.montant:
    if agence_destination.solde >= agence_destination.montant:
        expediteur.solde -= agence_destination.montant
'''
