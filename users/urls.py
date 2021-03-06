from django.contrib import admin
from django.urls import path, include
from .views import *
from .profil.views import *

urlpatterns = [
    path('sysadmin/register/', SysAdmin_UserCreate.as_view()),

    path('agent/register/', Agent_UserCreate.as_view()),
    path('agent/update/<int:pk>/', AgentUpdateAPIViews.as_view()),

    ###
    path('employe/register/', Employe_UserCreate.as_view()),
    path('employe/list/', EmployeListAPIViews.as_view()),
    path('employe/update/<int:pk>/', EmployeUpdateAPIViews.as_view()),

    ###
    path('responsable/register/', Responsable_UserCreate.as_view()),
    path('responsable/update/<int:pk>/', ResponsableUpdateAPIViews.as_view()),

    ###
    path('client_digiPay/register/', ClientDigiPay_UserCreate.as_view()),
    path('client_digiPay/update/<int:pk>/',
         ClientDigiPayUpdateAPIViews.as_view()),

    ###
    path('vendor/register/', Vendor_UserCreate.as_view()),
    path('vendor/update/<int:pk>/', VendorUpdateAPIViews.as_view()),
    path('vendor/func/valid-username/', valid_vendor_username),

    ###
    path('facturier/register/', Facturier_UserCreate.as_view()),
    path('facturier/update/<int:pk>/', FacturierUpdateAPIViews.as_view()),
    path('facturier/list/', FacturierListAPIViews.as_view()),

    path('auth-user/get/<int:pk>/', currentUserRetriveAPIViews.as_view()),
    path('password/update/<int:pk>/', UpdatePasswordView.as_view()),
    path('func/valid-PIN/', valid_code_PIN),

]
