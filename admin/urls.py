from rest_framework.routers import DefaultRouter
from django.urls import path, include
from quizes.views import (
    QuestionAdminViewSet,
    QuizAdminViewSet,
    QuizLevelViewSet,
    QuizVolumeViewSet,
    TagViewSet,
)
from user.views import DepartmentViewSet

router_v1 = DefaultRouter()
router_v1.register('levels', QuizLevelViewSet, basename='quiz-levels')
router_v1.register('tags', TagViewSet, basename='quiz-tags')
router_v1.register(
    r'quizes/(?P<quiz_id>[\d]+)/questions', QuestionAdminViewSet,
    basename='quiz-questions-list'
)
router_v1.register(
    r'quizes/(?P<quiz_id>[\d]+)/volumes', QuizVolumeViewSet,
    basename='quiz-volumes-list'
)
router_v1.register(
    'quizes/questions', QuestionAdminViewSet, basename='quiz-questions'
)
router_v1.register('quizes', QuizAdminViewSet, basename='quiz-admin')
router_v1.register('departments', DepartmentViewSet)

urlpatterns = [
    path('', include(router_v1.urls)),
]

urlpatterns += router_v1.urls
