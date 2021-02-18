from django.contrib import admin
from django.urls import path, include
from .views import *


urlpatterns = [
    path('agent/register/', Agent_UserCreate.as_view()),
    path('employe/register/', Employe_UserCreate.as_view()),
    path('responsable/register/', Responsable_UserCreate.as_view()),
    path('client_digiPay/register/', ClientDigiPay_UserCreate.as_view()),
    path('vendor/register/', Vendor_UserCreate.as_view()),
    path('employe/list/', EmployeListAPIViews.as_view()),
    path('current_user/get/<int:pk>/', currentUserRetriveAPIViews.as_view()),

]
