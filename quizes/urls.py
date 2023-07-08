from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    AnswerViewSet, QuizViewSet, StatisticViewSet, LastQuestionViewSet)

router_v1 = DefaultRouter()
router_v1.register('', QuizViewSet, basename='quizes')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('<int:id>/answer/', AnswerViewSet.as_view({'post': 'create'}),
         name='answer'),
    path('<int:id>/statistic/', StatisticViewSet.as_view({'get': 'list'}),
         name='statistic'),
    path('<int:id>/last/', LastQuestionViewSet.as_view({'get': 'retrieve'}),
         name='last-question'),
]

urlpatterns += router_v1.urls
