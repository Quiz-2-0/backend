from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    QuizViewSet,
    UserQuestionViewSet,
)

router_v1 = DefaultRouter()
router_v1.register('', QuizViewSet, basename='quizes')
router_v1.register(
     r'(?P<quiz_id>[\d]+)/answer', UserQuestionViewSet, basename='userquestion'
)

urlpatterns = [  
     path('', include(router_v1.urls)),
]
