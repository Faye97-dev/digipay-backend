from django.contrib import admin
from django.urls import path, include
from users.views import TokenObtainPairView, BlacklistTokenUpdateView, MyTokenObtainPairView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('users.urls')),
    #path('api/register/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/login/', MyTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('api/logout/', BlacklistTokenUpdateView.as_view(), name='blacklist'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('api.urls')),


]
