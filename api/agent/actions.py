from users.models import TransactionModel, Transfert, Compensation, Transaction, Notification, Responsable
from api.models import Agence
from api.serializers import TransactionFullSerializer
from users.serializers import CompensationFullSerializer
import uuid
from random import randint


def pre_compensation(agent, data):
    agence = Agence.objects.get(id=data['agence_destination'])
    responsable = Responsable.objects.filter(agence=agence)
    if len(responsable) != 0:
        responsable = responsable[0]
    else:
        return {'msg': "Aucun responsable d'agence n'est associé a cette agence !"}

    ##
    transaction_type = None
    msg_transaction_type = None
    #msg_transaction_type_ar = None
    if data['type_trans'] == 'versement':
        if agent.solde >= data['montant']:
            transaction_type = Transaction.COMP_VERSEMENT
            msg_transaction_type = 'versement'
            #msg_transaction_type_ar = 'دفع'
        else:
            return {'msg': "votre solde est insuffisant pour effectuer cette opération"}
    elif data['type_trans'] == 'retrait':
        transaction_type = Transaction.COMP_RETRAIT
        msg_transaction_type = 'retrait'
        #msg_transaction_type_ar = 'سحب'
    else:
        return {'msg': "le type de transaction est invalid !"}

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
        message="Voulez vous confirmer une compensation de " + msg_transaction_type + " de " + str(compensation.montant) + " MRU venant de l'agent : " +
        agent.name + "--"+agent.tel)

    # message_ar=f"{agent.tel}--{agent.name} أوقية من وكيل {compensation.montant} {msg_transaction_type_ar} هل تريد تأكيد تعويض")

    msgAgence.save()

    result = TransactionFullSerializer(transaction).data
    result['transaction'] = CompensationFullSerializer(compensation).data

    # print(' result ', result)
    return result
