from django.urls import include, path
from rest_framework.routers import DefaultRouter

from quizes.views import (
    AssignedAPIView,
    AssignedQuizDeleteAPIView,
    AssignedQuizUpdateAPIView,
    AssignedQuizViewSet,
    QuestionAdminViewSet,
    QuestionListAdminViewSet,
    QuizAdminViewSet,
    QuizImageViewSet,
    QuizLevelViewSet,
    QuizVolumeViewSet,
    TagViewSet,
)
from user.views import AdminMeAPIView, DepartmentViewSet, UserAdminViewSet, UserViewSet

router_v1 = DefaultRouter()
router_v1.register("levels", QuizLevelViewSet, basename="quiz-levels")
router_v1.register("tags", TagViewSet, basename="quiz-tags")
router_v1.register("quizes/images", QuizImageViewSet)
router_v1.register(
    r"quizes/(?P<quiz_id>[\d]+)/questions",
    QuestionAdminViewSet,
    basename="quiz-questions",
)
router_v1.register(
    r"quizes/(?P<quiz_id>[\d]+)/volumes",
    QuizVolumeViewSet,
    basename="quiz-volumes-list",
)
router_v1.register(
    r"quizes/(?P<quiz_id>[\d]+)/questions_list",
    QuestionListAdminViewSet,
    basename="quiz-questions-list",
)
router_v1.register("quizes", QuizAdminViewSet, basename="quiz-admin")
router_v1.register("users/departments", DepartmentViewSet)
router_v1.register("users/create", UserViewSet)
router_v1.register("users", UserAdminViewSet)
router_v1.register("users/departments", DepartmentViewSet)

urlpatterns = [
    path("quizes/assigned_list/", AssignedQuizViewSet.as_view()),
    path("quizes/assigned/", AssignedAPIView.as_view()),
    path("quizes/assigned/update/", AssignedQuizUpdateAPIView.as_view()),
    path("quizes/assigned/delete/", AssignedQuizDeleteAPIView.as_view()),
    path("users/me/", AdminMeAPIView.as_view()),
    path("", include(router_v1.urls)),
]

urlpatterns += router_v1.urls
