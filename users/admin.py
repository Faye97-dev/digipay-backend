from django.contrib import admin
from .models import MyUser, Responsable, Agent, Employee, Agent, Transaction, Transfert, Compensation, Client
from api.models import Agence, Commune
# Register your models here.
admin.site.register(MyUser)
admin.site.register(Agence)
admin.site.register(Responsable)
admin.site.register(Employee)
admin.site.register(Agent)
admin.site.register(Commune)

admin.site.register(Transaction)
admin.site.register(Transfert)
admin.site.register(Compensation)

admin.site.register(Client)
