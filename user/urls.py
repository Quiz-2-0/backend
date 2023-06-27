from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.routers import DefaultRouter

from django.urls import path, include

from user.views import UserViewSet, passwort_reset


router_v1 = DefaultRouter()
router_v1.register('create', UserViewSet)
urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('reset/', passwort_reset),
    path('', include(router_v1.urls)),
]
