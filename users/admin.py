from django.contrib import admin
from .models import MyUser, Responsable, Agent, Employee, Agent, Transaction, Transfert, Compensation, Client, Client_DigiPay, Vendor, Notification, Transfert_Direct, Pre_Transaction
from .models import Cagnote, Participants_Cagnote, Transfert_Cagnote, Group_Payement, Beneficiares_GrpPayement, SysAdmin
from api.models import Agence, Commune
# Register your models here.
admin.site.register(MyUser)
admin.site.register(Agence)
admin.site.register(Responsable)
admin.site.register(Employee)
admin.site.register(Agent)
admin.site.register(Commune)
admin.site.register(SysAdmin)

admin.site.register(Transaction)
admin.site.register(Transfert)
admin.site.register(Compensation)

admin.site.register(Client)
admin.site.register(Client_DigiPay)
admin.site.register(Vendor)

admin.site.register(Notification)
admin.site.register(Pre_Transaction)
admin.site.register(Transfert_Direct)

admin.site.register(Cagnote)
admin.site.register(Participants_Cagnote)
admin.site.register(Transfert_Cagnote)

admin.site.register(Group_Payement)
admin.site.register(Beneficiares_GrpPayement)
