from django.urls import path
from rest_framework import routers
from .views import *
from .actions import *
from .service import *
from .agence.views import *
router = routers.DefaultRouter()
router.register('client', ClientViewsets)
router.register('cloture', ClotureViewsets)

urlpatterns = [
    path('commune/list/', CommuneAPIViews.as_view()),

    path('notification/list/', NotificationListAPIViews.as_view()),

    path('agence/list/', AgenceListAPIViews.as_view()),
    path('agence/update/<int:pk>/', AgenceUpdateAPIViews.as_view()),
    path('agence/get/<int:pk>/', AgenceRetriveAPIViews.as_view()),

    path('transfert/list/', TransfertListAPIViews.as_view()),
    path('transfert/create/', TransfertCreateAPIViews.as_view()),
    path('transfert/update/<int:pk>/', TransfertUpdateAPIViews.as_view()),
    path('transfert/get/<int:pk>/', TransfertRetriveAPIViews.as_view()),
    path('transfert/delete/<int:pk>/', TransfertDeleteAPIViews.as_view()),

    path('compensation/list/', CompensationListAPIViews.as_view()),
    path('compensation/create/', CompensationCreateAPIViews.as_view()),
    path('compensation/update/<int:pk>/', CompensationUpdateAPIViews.as_view()),
    path('compensation/get/<int:pk>/', CompensationRetriveAPIViews.as_view()),

    path('transaction/list/', TransactionListAPIViews.as_view()),
    path('transaction/get/<int:pk>/', TransactionRetriveAPIViews.as_view()),
    path('transaction/create/', TransactionCreateAPIViews.as_view()),


    ###
    path('func/transaction/retrait_list/', transactions_a_retirer),
    path('func/transaction/secret_key_check/', check_secret_key),
    ###
    #path('func/transfert/add/', add_transfert),
    path('func/transfert/add/', agence_transfert),
    #path('func/transfert/error/', error_transfert),
    #path('func/retrait/add/', add_retrait),
    path('func/retrait/add/', agence_retrait),
    ##
    path('func/client_digiPay/check/', check_clientDigiPay),
    path('func/client_digiPay/envoie/', client_digiPay_envoie),
    # retrait dans une agence
    path('func/client/retrait_par_sms/', client_parSmsRetrait),

    ###
    path('', home),
]

urlpatterns += router.urls
