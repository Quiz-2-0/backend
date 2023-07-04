import base64
import uuid

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import exceptions, serializers

from django.core.files.base import ContentFile

from django.utils.translation import gettext_lazy as _

from user.models import User, Department
from user.utils import password_mail


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["role"] = serializers.CharField()

    def validate(self, attrs):
        result = super().validate(attrs)
        email = self.context['request'].data['email']
        role = self.context['request'].data['role']
        user = User.objects.get(email=email)
        result.pop('refresh')
        if role == user.role:
            return result
        raise exceptions.AuthenticationFailed(
            detail=_("Your role does not match")
        )


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = ('name',)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserCreateSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()
    department = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Department.objects.all()
    )

    class Meta:
        model = User
        fields = User.REQUIRED_FIELDS + (
            'patronymic', 'department', 'email', 'avatar', 'score'
        )

    def create(self, validated_data):
        password = str(uuid.uuid1())[:8]
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        password_mail(validated_data['email'], password)
        return user


class UserResetPasswordSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email']
