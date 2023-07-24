from rest_framework import serializers
from quizes.models import (
    Answer,
    Question,
    Quiz,
    # UserAnswer,
    Tag,
    Volume,
    # AssignedQuiz,
    QuizLevel,
    # UserQuestion,
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
        stat = Statistic.objects.filter(user=user, quiz=obj.quiz)
        user_question = stat.user_questions.filter(question=obj).first()
        return user_question.is_answered

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
        stat = Statistic.objects.get_or_create(
            user=user,
            quiz=obj,
        )
        return stat.is_passed

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


# class StatisticSerializer(serializers.ModelSerializer):
#     question = serializers.CharField(source='answer.question.text')
#     user_answer = serializers.CharField(source='answer.text')
#     right_answer = serializers.CharField(source='answer.question.right_answer')
#     isRight = serializers.BooleanField(source='answer.is_right')
#     explanation = serializers.CharField(source='answer.question.explanation')

#     class Meta:
#         model = UserAnswer
#         fields = [
#             "question",
#             "right_answer",
#             "user_answer",
#             "isRight",
#             "explanation",
#         ]


# class UserAnswerSerializer(serializers.ModelSerializer):
#     id = serializers.IntegerField(source='answer.id')

#     class Meta:
#         model = UserAnswer
#         fields = [
#             "id",
#         ]

# class UserAnswerSaveSerializer(serializers.ModelSerializer):

#     def create(self, validated_data):
#         answer = validated_data.pop("answer")
#         user_answer = UserAnswer.objects.filter(
#             **validated_data,
#             answer__question=answer.question
#         ).first()
#         if not user_answer:
#             user_answer = UserAnswer.objects.create(
#                 **validated_data,
#                 answer=answer
#             )
#         user_answer.answer = answer
#         user_answer.save()
#         answers = UserAnswer.objects.filter(**validated_data)
#         quiz = validated_data.get("quiz")
#         if (quiz.question_amount == answers.count() and
#                 answers.filter(answer__is_right=True).count() > 0):
#             assigned = AssignedQuiz.objects.filter(**validated_data).first()
#             if assigned:
#                 assigned.delete()
#         return user_answer

#     def validate(self, attrs):
#         quiz = attrs['quiz']
#         answer = attrs['answer']

#         if answer.question.quiz != quiz:
#             raise serializers.ValidationError({
#                 'error': 'Ответ не принадлежит данному квизу.'}
#             )

#         return attrs

#     class Meta:
#         model = UserAnswer
#         fields = [
#             "user",
#             "quiz",
#             "answer",
#         ]


class QuizLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizLevel
        fields = '__all__'
