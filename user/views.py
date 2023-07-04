import uuid
from django.shortcuts import get_object_or_404

from rest_framework import mixins, viewsets, status, generics
from rest_framework.response import Response

from user.models import User
from user.permission import AdminOrReadOnly
from user.serializers import UserCreateSerializer, UserResetPasswordSerializer
from user.utils import password_mail


class UserViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = UserCreateSerializer
    queryset = User.objects.all()


class UserResetPasswordViewSet(generics.CreateAPIView):
    serializer_class = UserResetPasswordSerializer
    queryset = User.objects.all()
    permission_classes = AdminOrReadOnly

    def post(self, request):
        email = request.data.get('email')
        user = get_object_or_404(User, email=email)
        password = str(uuid.uuid1())[:8]
        user.set_password(password)
        user.save()
        password_mail(email, password)
        return Response(status=status.HTTP_200_OK)


class UserGetViewSet(generics.RetrieveAPIView):
    serializer_class = UserCreateSerializer
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserCreateSerializer(request.user)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
