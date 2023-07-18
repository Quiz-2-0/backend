from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.routers import DefaultRouter

from django.urls import path, include

from user.views import (
    DepartmentViewSet,
    UserViewSet,
    UserResetPasswordViewSet,
    UserGetViewSet
)


router_v1 = DefaultRouter()
router_v1.register('create', UserViewSet)
router_v1.register('departments', DepartmentViewSet)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('reset/', UserResetPasswordViewSet.as_view()),
    path('me/', UserGetViewSet.as_view()),
    path('', include(router_v1.urls)),
]
