import base64
import re
import uuid

from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from quizes.models import AssignedQuiz
from ratings.models import Rating
from user.models import CustomUser, DefaultAvatar, Department, User
from user.utils import password_mail


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Сериализатор для получения пары токенов."""

    def __init__(self, *args, **kwargs):
        """Инициализирует сериализатор и добавляет поля "role" и "email"."""
        super().__init__(*args, **kwargs)
        self.fields["role"] = serializers.CharField()
        self.fields["email"] = serializers.EmailField()

    def validate(self, attrs):
        """
        Проверяет валидность данных.

        Если роль пользователя не совпадает с указанной ролью, вызывает исключение.
        """
        result = super().validate(attrs)
        email = self.context["request"].data["email"]
        validate_password = self.context["request"].data["password"]
        if re.findall(r"\s", validate_password):
            raise serializers.ValidationError("пароль содержит пробелы")
        role = self.context["request"].data["role"]
        user = User.objects.get(email=email)
        result.pop("refresh")
        if role == user.role:
            return result
        raise exceptions.AuthenticationFailed(detail=_("Your role does not match"))


class Base64ImageField(serializers.ImageField):
    """Класс для обработки изображений, закодированных в формате Base64."""

    def to_internal_value(self, data):
        """Преобразует данные из формата Base64 в изображение."""
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(
                base64.b64decode(imgstr), name=f"image{str(uuid.uuid1())[:6]}." + ext
            )
        return super().to_internal_value(data)


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя с определёнными полями."""

    id = serializers.IntegerField(required=False)
    firstName = serializers.CharField(max_length=150, required=True)
    lastName = serializers.CharField(max_length=150, required=True)
    patronymic = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(required=True)
    position = serializers.CharField(max_length=150, required=True)
    role = serializers.ChoiceField(choices=("EMP", "AD"), required=True)
    department = serializers.SlugRelatedField(
        slug_field="id", queryset=Department.objects.all(), required=True
    )

    class Meta:
        model = User
        fields = (
            "id",
            "patronymic",
            "department",
            "email",
            "firstName",
            "lastName",
            "position",
            "role",
        )

    def create(self, validated_data):
        """Создает и сохраняет нового пользователя с заданными данными."""
        password = str(uuid.uuid1())[:8]
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        _, _ = Rating.objects.get_or_create(user=user)
        password_mail(validated_data["email"], password)
        return user


class AdminMeSerializer(serializers.ModelSerializer):
    """Сериализатор для представления информации об администраторе."""

    class Meta:
        model = User
        fields = ["id", "firstName", "lastName", "email", "position", "avatar"]


class UserAdminSerializer(serializers.ModelSerializer):
    """Сериализатор."""

    department = serializers.SlugRelatedField(
        slug_field="name", queryset=Department.objects.all()
    )
    assigned = serializers.SerializerMethodField()
    count_passed = serializers.IntegerField(source="rating.count_passed")
    rating = serializers.IntegerField(source="rating.user_rating")

    # TODO annotate
    def get_assigned(self, obj):
        """Возвращает количество квизов, назначенных пользователю."""
        return AssignedQuiz.objects.filter(user=obj).count()

    class Meta:
        model = User
        fields = [
            "id",
            "firstName",
            "lastName",
            "patronymic",
            "email",
            "department",
            "position",
            "assigned",
            "count_passed",
            "rating",
        ]


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для представления информации о пользователе."""

    departament = serializers.CharField(source="department.name")
    pass_progress = serializers.IntegerField(source="rating.pass_progress")
    count_assigned = serializers.IntegerField(source="rating.count_assigned")
    count_passed = serializers.IntegerField(source="rating.count_passed")
    right_precent = serializers.IntegerField(source="rating.right_precent")
    level = serializers.IntegerField(source="rating.user_level.level")
    level_image = serializers.CharField(source="rating.user_level.image")
    level_description = serializers.CharField(source="rating.user_level.description")
    to_next_level = serializers.IntegerField(source="rating.to_next_level")
    in_this_level = serializers.IntegerField(source="rating.in_this_level")
    earned_in_level = serializers.IntegerField(source="rating.earned_in_level")

    class Meta:
        model = User
        fields = [
            "id",
            "firstName",
            "lastName",
            "patronymic",
            "avatar",
            "email",
            "role",
            "departament",
            "position",
            "pass_progress",
            "count_assigned",
            "count_passed",
            "right_precent",
            "level",
            "level_image",
            "level_description",
            "to_next_level",
            "in_this_level",
            "earned_in_level",
        ]


class UserResetPasswordSerializer(serializers.ModelSerializer):
    """Сериализатор для сброса пароля пользователя."""

    class Meta:
        model = User
        fields = ["email"]


class DepartmentSerializer(serializers.ModelSerializer):
    """Сериализатор для представления информации об отделе."""

    class Meta:
        model = Department
        fields = ["id", "name"]


class DefaultAvatarReadSerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка предустановленных аватарок."""

    class Meta:
        model = DefaultAvatar
        fields = "__all__"


class DefaultAvatarWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи аватара от пользователя."""

    avatar = Base64ImageField()

    class Meta:
        model = CustomUser
        fields = ("avatar",)
