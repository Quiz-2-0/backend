from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import QuizViewSet, AnswerViewSet, StatisticViewSet


router_v1 = DefaultRouter()
router_v1.register('', QuizViewSet, basename='quizes')
router_v1.register(
     '(?P<id>[\d]+)/statistic', StatisticViewSet, basename='statistic'
)

urlpatterns = [
     path('<int:id>/answer/', AnswerViewSet.as_view({'post': 'create'}),
          name='answer'),
     path('', include(router_v1.urls)),
]

urlpatterns += router_v1.urls
