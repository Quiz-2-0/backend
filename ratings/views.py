from rest_framework import mixins, permissions, response, status, viewsets
from rest_framework.decorators import action

from .models import Rating, UserAchivement
from .serializers import (
    RatingSerializer,
    RatingShortSerializer,
    UserAchivementSerializer,
    UserAchivementShortSerializer,
)


class UserAchivementViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Вьюсет для достижений пользователя."""

    serializer_class = UserAchivementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Возвращает достижения текущего пользователя."""
        return UserAchivement.objects.filter(user=self.request.user.id)

    @action(detail=False, methods=["get"])
    def short(self, request):
        """Возвращает последние 4 достижения пользователя."""
        user = request.user.id
        queryset = UserAchivement.objects.filter(user=user, achived=True).order_by(
            "-get_date"
        )[:4]
        serializer = UserAchivementShortSerializer(queryset, many=True)
        return response.Response(status=status.HTTP_200_OK, data=serializer.data)


class RatingViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Вьюсет для рейтинга пользователя."""

    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Возвращает рейтинг пользователей в том же отделе, что и пользователь."""
        departament = self.request.user.department.id
        return Rating.objects.filter(user__department=departament)

    @action(detail=False, methods=["get"])
    def short(self, request):
        """Возвращает рейтинг первых трех пользователей в отделе."""
        department = request.user.department.id
        queryset = Rating.objects.filter(user__department=department)[:3]
        serializer = RatingShortSerializer(queryset, many=True)
        return response.Response(status=status.HTTP_200_OK, data=serializer.data)
