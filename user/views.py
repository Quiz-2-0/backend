import uuid
from django.shortcuts import get_object_or_404

from rest_framework import mixins, viewsets, status, generics, permissions
from rest_framework.response import Response

from user.models import User, DefaultAvatar, Department
from user.serializers import (
    DefaultAvatarReadSerializer,
    DefaultAvatarWriteSerializer,
    DepartmentSerializer,
    UserCreateSerializer,
    UserResetPasswordSerializer,
    UserSerializer,
    UserAdminSerializer
)
from user.utils import password_mail
from user.permission import AdminOrReadOnly


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = UserCreateSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAdminUser]


class UserResetPasswordViewSet(generics.CreateAPIView):
    serializer_class = UserResetPasswordSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        user = get_object_or_404(User, email=email)
        password = str(uuid.uuid1())[:8]
        user.set_password(password)
        user.save()
        password_mail(email, password)
        return Response(status=status.HTTP_200_OK)


class UserGetViewSet(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserSerializer(request.user)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()
    permission_classes = [permissions.IsAdminUser]


class UserAdminViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = UserAdminSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAdminUser]


class AvatarListView(generics.ListCreateAPIView):
    """
    Представление для получения списка предустановленных аватаров и создания
    нового аватара.
    """
    queryset = DefaultAvatar.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return DefaultAvatarReadSerializer
        elif self.request.method == 'POST':
            return DefaultAvatarWriteSerializer

    def perform_create(self, serializer):
        # Добавление аватара текущему пользователю
        self.request.user.avatar = serializer.validated_data['avatar']
        self.request.user.save()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        avatar_url = request.user.avatar.url if request.user.avatar else None
        response.data['avatar'] = avatar_url
        return response
