from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (QuizLevelViewSet,
                    QuizViewSet,
                    TagViewSet,
                    # UserAnswerViewSet,
                    # StatisticViewSet, )
)

router_v1 = DefaultRouter()
router_v1.register('levels', QuizLevelViewSet, basename='quiz-levels')
router_v1.register('tags', TagViewSet, basename='quiz-tags')
router_v1.register('', QuizViewSet, basename='quizes')
# router_v1.register(
#      r'(?P<quiz_id>[\d]+)/answer', UserAnswerViewSet, basename='user_answer'
# )
# router_v1.register(
#      r'(?P<quiz_id>[\d]+)/statistic', StatisticViewSet, basename='statistic'
# )

urlpatterns = [  
     path('', include(router_v1.urls)),
]

urlpatterns += router_v1.urls
