from django.urls import path
from rest_framework import routers
from .views import *
from .actions import *

router = routers.DefaultRouter()
router.register('client', ClientViewsets)
router.register('cloture', ClotureViewsets)

urlpatterns = [
    path('commune/list/', CommuneAPIViews.as_view()),

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
    path('func/transfert/add/', add_transfert),
    path('func/transfert/error/', error_transfert),
    path('func/retrait/add/', add_retrait),
    path('func/transfert/add_atomic/', add_transfert_atomic),
    #path('', home),
]

urlpatterns += router.urls
