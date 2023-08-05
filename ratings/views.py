from rest_framework import permissions, viewsets, mixins, response, status
from .models import UserAchvment, Rating
from rest_framework.decorators import action
from .serializers import (
    UserAchivmentSerializer,
    UserAchivmentShortSerializer,
    RatingSerializer,
    RatingShortSerializer
)


class UserAchivmentViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = UserAchivmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserAchvment.objects.filter(user=self.request.user.id)

    @action(detail=False, methods=['get'])
    def short(self, request):
        user = request.user.id
        queryset = UserAchvment.objects.filter(
                user=user, achived=True
            ).order_by('-get_date')[:4]
        serializer = UserAchivmentShortSerializer(queryset, many=True)
        return response.Response(
            status=status.HTTP_200_OK, data=serializer.data
        )


class RatingViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = RatingSerializer,
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        departament = self.request.user.department.id
        return Rating.objects.filter(user__department=departament)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = RatingSerializer(queryset, many=True)
        return response.Response(serializer.data)

    @action(detail=False, methods=['get'])
    def short(self, request):
        departament = request.user.department.id
        queryset = Rating.objects.filter(
                user__department=departament
            )[:3]
        serializer = RatingShortSerializer(queryset, many=True)
        return response.Response(
            status=status.HTTP_200_OK, data=serializer.data
        )