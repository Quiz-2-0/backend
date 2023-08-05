from rest_framework import serializers
from .models import (
    Rating,
    UserAchvment
)


class UserAchivmentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='achivment.name')
    description = serializers.CharField(source='achivment.description')
    image = serializers.CharField(source='achivment.image')

    class Meta:
        model = UserAchvment
        fields = [
            'id',
            'points_now',
            'points_to_get',
            'name',
            'description',
            'image',
            'achived',
        ]


class UserAchivmentShortSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='achivment.name')
    image = serializers.ImageField(source='achivment.image')

    class Meta:
        model = UserAchvment
        fields = [
            'name',
            'image',
        ]


class RatingSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(source='user.firstName')
    lastName = serializers.CharField(source='user.lastName')
    avatar = serializers.ImageField(source='user.avatar')

    class Meta:
        model = Rating
        fields = [
            'firstName',
            'lastName',
            'avatar',
            'count_passed',
            'user_level',
            'user_rating',
        ]


class RatingShortSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(source='user.firstName')
    lastName = serializers.CharField(source='user.lastName')
    avatar = serializers.ImageField(source='user.avatar')

    class Meta:
        model = Rating
        fields = [
            'firstName',
            'lastName',
            'avatar',
            'user_rating',
        ]
