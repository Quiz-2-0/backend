from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.routers import DefaultRouter

from django.urls import path, include

from user.views import (
    AvatarListView,
    UserResetPasswordViewSet,
    UserGetViewSet,
)
from ratings.views import UserAchivmentViewSet, RatingViewSet


router_v1 = DefaultRouter()
router_v1.register('achivments', UserAchivmentViewSet, basename='achivments')
router_v1.register('ratings', RatingViewSet, basename='ratings')

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('avatar/', AvatarListView.as_view(), name='avatars'),
    path('reset/', UserResetPasswordViewSet.as_view()),
    path('me/', UserGetViewSet.as_view()),
    path('', include(router_v1.urls)),
]
