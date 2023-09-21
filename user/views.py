import uuid

from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, permissions, status, viewsets
from rest_framework.response import Response

from user.models import DefaultAvatar, Department, User
from user.serializers import (
    AdminMeSerializer,
    DefaultAvatarReadSerializer,
    DefaultAvatarWriteSerializer,
    DepartmentSerializer,
    UserAdminSerializer,
    UserCreateSerializer,
    UserResetPasswordSerializer,
    UserSerializer,
)
from user.utils import password_mail


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Представление для создания, обновления и удаления пользователей."""

    serializer_class = UserCreateSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAdminUser]


class UserResetPasswordViewSet(generics.CreateAPIView):
    """Вьюсет для сброса пароля пользователя."""

    serializer_class = UserResetPasswordSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Переопределение метода POST для сброса пароля пользователя."""
        email = request.data.get("email")
        user = get_object_or_404(User, email=email)
        password = str(uuid.uuid1())[:8]
        user.set_password(password)
        user.save()
        password_mail(email, password)
        return Response(status=status.HTTP_200_OK)


class UserGetViewSet(generics.RetrieveAPIView):
    """Вьюсет для получения информации о пользователе."""

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Проверка доступа пользователя для получения информации."""
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserSerializer(request.user)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class DepartmentViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с отделами."""

    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()
    permission_classes = [permissions.IsAdminUser]


class UserAdminViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    """Вьюсет для работы с пользователями с ролью администратора."""

    serializer_class = UserAdminSerializer
    queryset = User.objects.filter(role="EMP").all()
    permission_classes = [permissions.IsAdminUser]


class AvatarListView(generics.ListCreateAPIView):
    """
    Представление для получения списка предустановленных аватаров.

    И для создания нового аватара.
    """

    queryset = DefaultAvatar.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Метод для определения класса сериализатора в зависимости от запроса."""
        if self.request.method == "GET":
            return DefaultAvatarReadSerializer
        elif self.request.method == "POST":
            return DefaultAvatarWriteSerializer

    def perform_create(self, serializer):
        """Метод для добавления аватара текущему пользователю."""
        self.request.user.avatar = serializer.validated_data["avatar"]
        self.request.user.save()

    def create(self, request, *args, **kwargs):
        """Метод для создания нового аватара."""
        response = super().create(request, *args, **kwargs)
        avatar_url = request.user.avatar.url if request.user.avatar else None
        response.data["avatar"] = avatar_url
        return response


class AdminMeAPIView(generics.RetrieveAPIView):
    """Представление для получения информации об администраторе."""

    serializer_class = AdminMeSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        """Проверка доступа пользователя для получения информации."""
        if not request.user.is_staff:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = AdminMeSerializer(request.user)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
