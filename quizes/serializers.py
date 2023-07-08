from rest_framework import serializers
from quizes.models import (
    Answer, Question, Quiz, Statistic, Tag, Volume, LastQuestion)


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

    class Meta:
        model = Question
        fields = [
            "id",
            "image",
            "text",
            "answers",
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
    class Meta:
        model = Answer
        fields = [
            "text",
            "is_right",
            "explanation"
        ]


class StatisticQuestionSerializer(serializers.ModelSerializer):
    answers = StatisticAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            "text",
            "answers",
        ]


class StatisticSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    quiz = QuizSerializer()
    questions = StatisticQuestionSerializer(
        source='quiz.questions', many=True, read_only=True)

    class Meta:
        model = Statistic
        fields = [
            "id",
            "user",
            "quiz",
            "questions",
            "wrong_answers",
        ]


class LastQuestionSerializer(serializers.ModelSerializer):
    statistic = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = LastQuestion
        fields = ['id', 'statistic', 'question']

    def create(self, validated_data):
        statistic = validated_data['statistic']
        question = validated_data['question']
        last_question = LastQuestion.objects.create(
            statistic=statistic,
            question=question
        )
        return last_question
