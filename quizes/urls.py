from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (
    NotComplitedQuizViewSet,
    QuizViewSet,
    StatisticApiView,
    UserQuestionViewSet,
)

router_v1 = DefaultRouter()
router_v1.register(
    "not_complited", NotComplitedQuizViewSet, basename="not_complited_quizes"
)
router_v1.register("", QuizViewSet, basename="quizes")
router_v1.register(
    r"(?P<quiz_id>[\d]+)/answer", UserQuestionViewSet, basename="userquestion"
)

urlpatterns = [
    re_path(r"(?P<quiz_id>[\d]+)/statistic", StatisticApiView.as_view()),
    path("", include(router_v1.urls)),
]
