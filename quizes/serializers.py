from rest_framework import serializers
from django.shortcuts import get_object_or_404
from quizes.models import (
    Answer,
    Question,
    Quiz,
    UserAnswer,
    Tag,
    Volume,
    AssignedQuiz
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

    class Meta:
        model = Answer
        fields = [
            "id",
            "text",
            "image",
        ]


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    is_answered = serializers.SerializerMethodField()

    def get_is_answered(self, obj):
        user = self.context['request'].user
        return UserAnswer.objects.filter(
            user=user,
            quiz=obj.quiz,
            answer__question=obj
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
    isPassed = serializers.SerializerMethodField()
    appointed = serializers.BooleanField()

    def get_isPassed(self, obj):
        user = self.context['request'].user
        questions = obj.question_amount
        right_answers = UserAnswer.objects.filter(
            user=user,
            quiz=obj,
            answer__is_right=True
        ).count()
        return questions == right_answers

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


class StatisticSerializer(serializers.ModelSerializer):
    question = serializers.CharField(source='answer.question.text')
    user_answer = serializers.CharField(source='answer.text')
    right_answer = serializers.CharField(source='answer.question.right_answer')
    isRight = serializers.BooleanField(source='answer.is_right')
    explanation = serializers.CharField(source='answer.question.explanation')

    class Meta:
        model = UserAnswer
        fields = [
            "question",
            "right_answer",
            "user_answer",
            "isRight",
            "explanation",
        ]


class UserAnswerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='answer.id')

    class Meta:
        model = UserAnswer
        fields = [
            "id",
        ]


class UserAnswerSaveSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        answer = validated_data.pop("answer")
        if UserAnswer.objects.filter(
            **validated_data,
            answer__question=answer.question
        ).exists():
            user_answer = get_object_or_404(
                UserAnswer,
                **validated_data,
                answer__question=answer.question
            )
            user_answer.answer = answer
            user_answer.save()
        else:
            user_answer = UserAnswer.objects.create(
                **validated_data, answer=answer
            )
        right_answers = UserAnswer.objects.filter(
            **validated_data,
            answer__is_right=True
        ).count()
        if answer.question.quiz.question_amount == right_answers:
            assigned = AssignedQuiz.objects.filter(**validated_data).first()
            if assigned:
                assigned.delete()
        return user_answer

    class Meta:
        model = UserAnswer
        fields = [
            "user",
            "quiz",
            "answer",
        ]
