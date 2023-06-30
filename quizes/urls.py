from rest_framework.routers import DefaultRouter

from django.urls import path, include

from .views import QuizViewSet, StatisticViewSet


router_v1 = DefaultRouter()
router_v1.register('', QuizViewSet, basename='quizes')
urlpatterns = [
    path('statistic/', StatisticViewSet.as_view(
        {'post': 'collect_statistic'}
    ), name='collect_statistic'),
    path('', include(router_v1.urls)),
]
