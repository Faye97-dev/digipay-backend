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
#router.register('cloture', ClotureViewsets)

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

    path('cagnote/create/', createCagnote),
    path('cagnote/list/', getCagnoteList),
    path('cagnote/check-client_digipay/', check_clientDigiPay_newCagnote),
    path('cagnote/delete/', client_delete_cagnote),


    path('grp-payement/list/', Grp_PayementListAPIViews.as_view()),
    path('grp-payement/create/', Grp_PayementCreateAPIViews.as_view()),
    path('grp-payement/delete/<int:pk>/', Grp_PayementDeleteAPIViews.as_view()),
    path('grp-payement/check-client_digipay/',
         check_clientDigiPay_grpPayement),

    path('beneficiaire-grp_payement/list/', getBeneficiares_grpPayement),
    path('beneficiaire-grp_payement/create/',
         client_add_beneficiaire_grpPayement),
    path('beneficiaire-grp_payement/update/<int:pk>/',
         client_update_beneficiaire_grpPayement),
    path('beneficiaire-grp_payement/delete/<int:pk>/',
         client_delete_beneficiaire_grpPayement),

    ###
    #path('func/transfert/add/', add_transfert),
    #path('func/transfert/error/', error_transfert),
    #path('func/retrait/add/', add_retrait),

    # agence
    path('func/transaction/retrait-list/', transactions_a_retirer),
    path('func/transaction/valid-secret-key/', check_secret_key),
    path('func/transaction/valid-compensation/', valid_compensation),
    path('func/transaction/beneficiaires-payement_masse/',
         getBeneficiares_by_codeGrpPayement),

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
    path('func/client_digiPay/valid-cagnote-code/', check_cagnote_byId),
    path('func/client_digiPay/participer-cagnote/', client_participer_cagnote),
    path('func/client_digiPay/update-participation/',
         client_update_participation_cagnote),
    path('func/client_digiPay/cloturer-cagnote/', client_cloturer_cagnote),
    path('func/client_digiPay/participants-cagnote/', getParticipantsCagnote),
    path('func/client_digiPay/payement-masse/', client_payement_masse),

    ##
    path('func/client_digiPay/payement-somelec/', client_somelec_payement),
    path('func/client_digiPay/reclamation-somelec/', client_somelec_reclamation),


    # Digipay vendor
    path('func/vendor/gen-code-payement/', random_code_payement),
    path('func/vendor/valid-code-payement/', check_codePayement_vendor),
    path('func/vendor/payement/', vendor_payement),
    path('func/vendor/payback/', vendor_payback),
    path('func/vendor/valid-code-transaction/', check_codeTransaction),
    path('func/vendor/livraison-client/', livraison_client),
    path('func/vendor/livraison-vendor/', livraison_vendor),
    path('func/vendor/valid-vendor-id/', vendor_check_VendorId),
    path('func/vendor/fast-payement/', vendor_fast_payement),

    ###

    # agence compensation
    path('func/agent/pre-compensation/', demande_compensation),
    #path('', home),

    # statistiques
    path('func/profil/statistique/<int:pk>/', profile_statistiques),
]

urlpatterns += router.urls
