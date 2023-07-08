from rest_framework import serializers
from django.shortcuts import get_object_or_404
from quizes.models import (
    Answer,
    Question,
    Quiz,
    UserAnswer,
    Tag,
    Volume,
    Statistic
)


class VolumeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Volume
        fields = [
            "name",
            "description",
        ]


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = [
            "id",
            "name",
            "color"
        ]


class AnswerSerializer(serializers.ModelSerializer):
    isAnswerRight = serializers.BooleanField(source='is_right')

    class Meta:
        model = Answer
        fields = [
            "id",
            "text",
            "image",
            "isAnswerRight"
        ]


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    is_answered = serializers.SerializerMethodField()

    def get_is_answered(self, obj):
        user = self.context['request'].user
        statistic = get_object_or_404(Statistic, user=user, quiz=obj.quiz)
        return UserAnswer.objects.filter(
            statistic=statistic, answer__question=obj
        ).exists()

    class Meta:
        model = Question
        fields = [
            "id",
            "image",
            "text",
            "answers",
            "is_answered"
        ]


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    directory = serializers.StringRelatedField()
    level = serializers.StringRelatedField()
    tags = TagSerializer(many=True, read_only=True)
    volumes = VolumeSerializer(many=True, read_only=True)
    isPassed = serializers.BooleanField()
    appointed = serializers.BooleanField()

    class Meta:
        model = Quiz
        fields = [
            "id",
            "image",
            "description",
            "directory",
            "name",
            "duration",
            "level",
            "question_amount",
            "tags",
            "questions",
            "volumes",
            "isPassed",
            "appointed"
        ]


class StatisticAnswerSerializer(serializers.ModelSerializer):
    question = serializers.CharField(source='answer.question.text')
    answer = serializers.StringRelatedField()
    isRight = serializers.BooleanField(source='answer.is_right')
    explanation = serializers.CharField(source='answer.question.explanation')

    class Meta:
        model = UserAnswer
        fields = [
            "question",
            "answer",
            "isRight",
            "explanation",
        ]
