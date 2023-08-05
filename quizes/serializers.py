from rest_framework import serializers
from django.shortcuts import get_object_or_404
from quizes.models import (
    Answer,
    Question,
    Quiz,
    Tag,
    Volume,
    QuizLevel,
    UserAnswerList,
    UserAnswer,
    UserQuestion,
    Statistic,
    AnswerList,
    AssignedQuiz
)


class VolumeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Volume
        fields = [
            'name',
            'description',
        ]


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = [
            'id',
            'name',
            'color'
        ]


class AnswerListSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnswerList
        fields = [
            'id',
            'text',
        ]


class AnswerSerializer(serializers.ModelSerializer):
    answers_list = AnswerListSerializer(many=True, read_only=True)

    class Meta:
        model = Answer
        fields = [
            'id',
            'text',
            'image',
            'answers_list'
        ]


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    is_answered = serializers.SerializerMethodField()

    # TODO annotate
    def get_is_answered(self, obj):
        user = self.context['request'].user
        stat = Statistic.objects.get_or_create(user=user, quiz=obj.quiz)
        user_question = UserQuestion.objects.filter(
            statistic=stat[0].id, question=obj
        ).first()
        return True if user_question else False

    class Meta:
        model = Question
        fields = [
            'id',
            'question_type',
            'image',
            'text',
            'answers',
            'is_answered'
        ]


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    directory = serializers.StringRelatedField()
    level = serializers.StringRelatedField()
    tags = TagSerializer(many=True, read_only=True)
    volumes = VolumeSerializer(many=True, read_only=True)
    isPassed = serializers.SerializerMethodField()
    appointed = serializers.BooleanField()

    # TODO annotate
    def get_isPassed(self, obj):
        user = self.context['request'].user
        stat, _ = Statistic.objects.get_or_create(
            user=user,
            quiz=obj,
        )
        return stat.is_passed

    class Meta:
        model = Quiz
        fields = [
            'id',
            'image',
            'description',
            'directory',
            'name',
            'duration',
            'level',
            'question_amount',
            'tags',
            'questions',
            'volumes',
            'isPassed',
            'appointed'
        ]


class QuizLevelSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuizLevel
        fields = '__all__'


class UserAnswerListSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserAnswerList
        fields = [
            'answer_list',
        ]


class UserAnswerSerializer(serializers.ModelSerializer):
    answer_list = UserAnswerListSerializer(many=True)

    class Meta:
        model = UserAnswer
        fields = [
            'answer',
            'answer_text',
            'answer_list'
        ]


class UserQuestionSerializer(serializers.ModelSerializer):
    answers = UserAnswerSerializer(many=True)
    id = serializers.IntegerField(source='question.id')
    question_type = serializers.CharField(source='question.question_type')

    class Meta:
        model = UserQuestion
        fields = [
            'id',
            'question_type',
            'response_time',
            'answers'
        ]


class UserQuestionSaveSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        # TODO подумать над валиидацией
        print(attrs)
        statistic = attrs['statistic']
        question = attrs['question']
        if question.quiz != statistic.quiz:
            raise serializers.ValidationError({
                'error': 'Ответ не принадлежит данному квизу.'}
            )
        answers = self.initial_data.pop('answers')
        attrs['answers'] = answers
        return attrs

    def create(self, validated_data):
        answers = validated_data.pop('answers')
        data = {
            'statistic': validated_data.get('statistic'),
            'question': validated_data.get('question')
        }
        # TODO продумать обновление а не удаление
        user_question = UserQuestion.objects.filter(**data).first()
        if user_question:
            user_question.delete()
        user_question = UserQuestion.objects.create(**validated_data)
        for ans in answers:
            answers_list = ans.pop('answer_list')
            answer = get_object_or_404(Answer, id=ans.pop('answer'))
            user_answer = UserAnswer.objects.create(
                user_question=user_question,
                answer=answer,
                **ans
            )
            for ans_list in answers_list:
                answer_list = get_object_or_404(
                    AnswerList,
                    id=ans_list.pop('answer_list')
                )
                UserAnswerList.objects.create(
                    user_answer=user_answer,
                    answer_list=answer_list
                )
        user_question.set_is_right
        # TODO удаление квизов из назначенных
        return user_question

    class Meta:
        model = UserQuestion
        fields = [
            'id',
            'statistic',
            'question',
            'response_time',
        ]


class AssignedSerializer(serializers.ModelSerializer):

    class Meta:
        model = AssignedQuiz
        fields = [
            'user',
            'quiz',
        ]