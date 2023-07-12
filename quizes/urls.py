from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import QuizViewSet, UserAnswerViewSet, StatisticViewSet


router_v1 = DefaultRouter()
router_v1.register('', QuizViewSet, basename='quizes')
router_v1.register(
     '(?P<quiz_id>[\d]+)/answer', UserAnswerViewSet, basename='user_unswer'
)
router_v1.register(
     '(?P<quiz_id>[\d]+)/statistic', StatisticViewSet, basename='statistic'
)

urlpatterns = [  
     path('', include(router_v1.urls)),
]

urlpatterns += router_v1.urls
