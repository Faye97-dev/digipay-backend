from django.urls import path
from rest_framework import routers
from .views import *
from .actions import *
from .service import *
from .agence.views import *
from .client.views import *
from .vendor.views import *
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
    #path('func/transfert/error/', error_transfert),
    #path('func/retrait/add/', add_retrait),

    path('func/transfert/add/', agence_transfert),
    path('func/retrait/add/', agence_retrait),
    path('func/client_digiPay_vendor/check/', check_byRole_ClientVendor),
    path('func/recharge/add/', agence_recharge),
    path('func/client_digiPay_vendor/retrait/',
         agence_retrait_par_codeConfirmation),

    ##
    path('func/client_digiPay/check/', check_clientDigiPay),
    path('func/client_digiPay/envoie/', client_digiPay_envoie),
    # client_digipay and vendor
    path('func/client_digiPay/retrait/', random_code_retrait),
    path('func/client_digiPay/check_codePayement/', check_codePayement),
    path('func/client_digiPay/payement/', client_payement),
    path('func/client_digiPay/achat_credit/', client_achat_credit),

    # retrait dans une agence par un anonyme
    path('func/client/retrait_par_sms/', client_parSmsRetrait),

    ##
    path('func/vendor/gen_codePayement/', random_code_payement),
    path('func/vendor/check_codePayement/', check_codePayement_vendor),
    path('func/vendor/payement/', vendor_payement),
    path('func/vendor/payback/', vendor_payback),
    path('func/vendor/check_codeTransaction/', check_codeTransaction),
    ###
    path('', home),
]

urlpatterns += router.urls
