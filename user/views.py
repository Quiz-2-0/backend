import uuid
from django.shortcuts import get_object_or_404

from rest_framework import mixins, viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from user.models import User
from user.permission import AdminOrReadOnly
from user.serializers import UserCreateSerializer
from user.utils import password_mail


class UserViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = UserCreateSerializer
    queryset = User.objects.all()


@api_view(['POST'])
@permission_classes([AdminOrReadOnly])
def passwort_reset(request):
    email = request.data.get('email')
    user = get_object_or_404(User, email=email)
    password = str(uuid.uuid1())[:8]
    user.set_password(password)
    user.save()
    password_mail(email, password)
    return Response(status=status.HTTP_200_OK)
