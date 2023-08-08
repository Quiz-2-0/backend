import uuid
from django.shortcuts import get_object_or_404

from rest_framework import mixins, viewsets, status, generics, permissions
from rest_framework.response import Response

from user.models import User, DefaultAvatar, Department
from user.serializers import (
    UserCreateSerializer,
    UserResetPasswordSerializer,
    DefaultAvatarSerializer,
    DepartmentSerializer,
    UserSerializer,
    UserAdminSerializer
)
from user.utils import password_mail
from user.permission import AdminOrReadOnly


class UserViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = UserCreateSerializer
    queryset = User.objects.all()


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

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserSerializer(request.user)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()
    permission_classes = (AdminOrReadOnly,)


class UserAdminViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = UserAdminSerializer
    queryset = User.objects.all()


class DefaultAvatarListView(generics.ListAPIView):
    """
    Представление для получения списка предустановленных аватаров.
    """
    queryset = DefaultAvatar.objects.all()
    serializer_class = DefaultAvatarSerializer


class UserAvatarUploadView(generics.CreateAPIView):
    """
    Представление для сохранения загруженного пользователем аватара.
    """
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()
