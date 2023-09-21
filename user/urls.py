from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView

from ratings.views import RatingViewSet, UserAchivementViewSet
from user.views import AvatarListView, UserGetViewSet, UserResetPasswordViewSet

router_v1 = DefaultRouter()
router_v1.register("achivements", UserAchivementViewSet, basename="achivements")
router_v1.register("ratings", RatingViewSet, basename="ratings")

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("avatar/", AvatarListView.as_view(), name="avatars"),
    path("reset/", UserResetPasswordViewSet.as_view()),
    path("me/", UserGetViewSet.as_view()),
    path("", include(router_v1.urls)),
]
