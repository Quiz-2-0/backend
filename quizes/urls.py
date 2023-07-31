from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    QuestionAdminViewSet,
    QuizAdminViewSet,
    QuizLevelViewSet,
    QuizViewSet,
    TagViewSet,
    UserQuestionViewSet,
)

router_v1 = DefaultRouter()
router_v1.register('admin/levels', QuizLevelViewSet, basename='quiz-levels')
router_v1.register('admin/tags', TagViewSet, basename='quiz-tags')
router_v1.register('admin', QuizAdminViewSet, basename='quiz-admin')
router_v1.register(
    'admin/quizes/questions', QuestionAdminViewSet, basename='quiz-questions'
)
router_v1.register('', QuizViewSet, basename='quizes')
router_v1.register(
     r'(?P<quiz_id>[\d]+)/answer', UserQuestionViewSet, basename='userquestion'
)
router_v1.register(
    r'admin/quizes/(?P<quiz_id>[\d]+)/questions', QuestionAdminViewSet,
    basename='quiz-questions-list'
)

urlpatterns = [  
     path('', include(router_v1.urls)),
]

urlpatterns += router_v1.urls
