from users.models import TransactionModel, Transfert, Compensation, Transaction, Notification, Responsable
from api.models import Agence
from api.serializers import TransactionFullSerializer
from users.serializers import CompensationFullSerializer
import uuid
from random import randint


def pre_compensation(agent, data):
    transaction_type = None
    msg_transaction_type = None
    if data['type_trans'] == 'versement':
        transaction_type = Transaction.COMP_VERSEMENT
        msg_transaction_type = 'Versement'
    elif data['type_trans'] == 'retrait':
        transaction_type = Transaction.COMP_RETRAIT
        msg_transaction_type = 'Retrait'
    else:
        return {'msg': "le type de transaction est invalid !"}
    ##
    agence = Agence.objects.get(id=data['agence_destination'])
    responsable = Responsable.objects.filter(agence=agence)
    if len(responsable) != 0:
        responsable = responsable[0]
    else:
        return {'msg': "Aucun responsable d'agence n'est associé a cette agence !"}
    ##
    compensation = Compensation(agence=agence,
                                agent=agent,
                                status=TransactionModel.TO_VALIDATE,
                                montant=data['montant'],
                                remarque=data['remarque'])
    compensation.save()

    transaction = Transaction(transaction=compensation, type_transaction=transaction_type,
                              date=compensation.date_creation)
    transaction.save()

    # notifications

    msgAgence = Notification(
        user=responsable, transaction=compensation, status=Notification.DEMANDE_COMPENSATION,
        message="Voulez vous confirmer une compensation de " + msg_transaction_type + " de " + str(compensation.montant) + " MRU venant de l'agent : "+agent.name + "--"+agent.tel)
    msgAgence.save()

    result = TransactionFullSerializer(transaction).data
    result['transaction'] = CompensationFullSerializer(compensation).data

    # print(' result ', result)
    return result
