from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
     QuizLevelViewSet,
     QuizViewSet,
     TagViewSet,
     UserQuestionViewSet,
     AssignedQuizViewSet
)


router_v1 = DefaultRouter()
router_v1.register('admin/levels', QuizLevelViewSet, basename='quiz-levels')
router_v1.register('admin/tags', TagViewSet, basename='quiz-tags')
router_v1.register('admin/assigned', AssignedQuizViewSet)
router_v1.register('', QuizViewSet, basename='quizes')
router_v1.register(
     r'(?P<quiz_id>[\d]+)/answer', UserQuestionViewSet, basename='userquestion'
)

urlpatterns = [
     path('', include(router_v1.urls)),
]

urlpatterns += router_v1.urls
