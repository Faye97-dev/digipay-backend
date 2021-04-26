from django.urls import path
from rest_framework import routers
from .views import *
from .actions import check_secret_key
from .service import check_clientDigiPay, profile_statistiques
from .agence.views import *
from .client.views import *
from .vendor.views import *
from .agent.views import *
router = routers.DefaultRouter()
router.register('client', ClientViewsets)
router.register('cloture', ClotureViewsets)

urlpatterns = [
    path('commune/list/', CommuneAPIViews.as_view()),

    path('notification/list/', NotificationListAPIViews.as_view()),
    path('notification/update/<int:pk>/', NotificationUpdateAPIViews.as_view()),

    path('agence/list/', AgenceListAPIViews.as_view()),
    path('agence/update/<int:pk>/', AgenceUpdateAPIViews.as_view()),
    path('agence/get/<int:pk>/', AgenceRetriveAPIViews.as_view()),

    path('transfert/list/', TransfertListAPIViews.as_view()),
    path('transfert/create/', TransfertCreateAPIViews.as_view()),
    path('transfert/update/<int:pk>/', TransfertUpdateAPIViews.as_view()),
    path('transfert/get/<int:pk>/', TransfertRetriveAPIViews.as_view()),
    path('transfert/delete/<int:pk>/', TransfertDeleteAPIViews.as_view()),

    #path('compensation/list/', CompensationListAPIViews.as_view()),
    path('compensation/list/', TransactionCompensationListAPIViews.as_view()),
    path('compensation/create/', CompensationCreateAPIViews.as_view()),
    path('compensation/update/<int:pk>/', CompensationUpdateAPIViews.as_view()),
    path('compensation/get/<int:pk>/', CompensationRetriveAPIViews.as_view()),

    path('transaction/list/', TransactionListAPIViews.as_view()),
    path('transaction/get/<int:pk>/', TransactionRetriveAPIViews.as_view()),
    path('transaction/create/', TransactionCreateAPIViews.as_view()),

    ###
    #path('func/transfert/add/', add_transfert),
    #path('func/transfert/error/', error_transfert),
    #path('func/retrait/add/', add_retrait),

    # agence
    path('func/transaction/retrait-list/', transactions_a_retirer),
    path('func/transaction/valid-secret-key/', check_secret_key),
    path('func/transaction/valid-compensation/', valid_compensation),
    path('func/client/valid-client-tel/', check_existant_tel),
    # retrait dans une agence par un anonyme
    path('func/client/retrait-by-sms/', client_parSmsRetrait),
    path('func/client/check/', check_client_anonyme),


    path('func/transfert/add/', agence_transfert),
    path('func/retrait/add/', agence_retrait),
    path('func/recharge/add/', agence_recharge),
    path('func/clientdigiPay-and-vendor/check/', check_byRole_ClientVendor),
    path('func/clientdigiPay-and-vendor/retrait/',
         agence_retrait_par_codeConfirmation),

    # Digipay client
    path('func/client_digiPay/check/', check_clientDigiPay),
    path('func/client_digiPay/envoie/', client_digiPay_envoie),
    # retrait client_digipay and vendor
    path('func/client_digiPay/retrait/', random_code_retrait),
    path('func/client_digiPay/valid-code-payement/', check_codePayement),
    path('func/client_digiPay/valid-vendor-id/', client_check_VendorId),
    path('func/client_digiPay/fast-payement/', client_fast_payement),
    path('func/client_digiPay/payement/', client_payement),
    path('func/client_digiPay/achat-credit/', client_achat_credit),


    # Digipay vendor
    path('func/vendor/gen-code-payement/', random_code_payement),
    path('func/vendor/valid-code-payement/', check_codePayement_vendor),
    path('func/vendor/payement/', vendor_payement),
    path('func/vendor/payback/', vendor_payback),
    path('func/vendor/valid-code-transaction/', check_codeTransaction),
    path('func/vendor/livraison-client/', livraison_client),
    ###

    # agence compensation
    path('func/agent/pre-compensation/', demande_compensation),
    #path('', home),

    # statistiques
    path('func/profil/statistique/<int:pk>/', profile_statistiques),
]

urlpatterns += router.urls


# todo :
# block e-commerce and fast payement for vendor ,
