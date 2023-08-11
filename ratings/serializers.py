from rest_framework import serializers
from .models import (
    Rating,
    UserAchivement
)


class UserAchivementSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='achivement.name')
    description = serializers.CharField(source='achivement.description')
    image = serializers.CharField(source='achivement.image')

    class Meta:
        model = UserAchivement
        fields = [
            'id',
            'points_now',
            'points_to_get',
            'name',
            'description',
            'image',
            'achived',
        ]


class UserAchivementShortSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='achivement.name')
    image = serializers.ImageField(source='achivement.image')

    class Meta:
        model = UserAchivement
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
            'id',
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
            'id',
            'firstName',
            'lastName',
            'avatar',
            'user_rating',
        ]
