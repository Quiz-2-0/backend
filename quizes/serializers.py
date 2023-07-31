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
    AnswerList
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
    answers_list = AnswerListSerializer(many=True)

    class Meta:
        model = Answer
        fields = [
            'id',
            'text',
            'image',
            'answers_list',
        ]

    # Переопределён метод create для обработки вложенных данных (answers_list)
    def create(self, validated_data):
        answers_list_data = validated_data.pop('answers_list', [])
        answer = Answer.objects.create(**validated_data)
        for answer_list_data in answers_list_data:
            AnswerList.objects.create(answer=answer, **answer_list_data)
        return answer


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    is_answered = serializers.SerializerMethodField()

    # TODO annotate
    def get_is_answered(self, obj):
        user = self.context['request'].user
        stat = Statistic.objects.get_or_create(user=user, quiz=obj.quiz)
        print(stat[0])
        user_question = UserQuestion.objects.filter(
            statistic=stat[0].id, question=obj
        ).first()
        return user_question.is_answered if user_question else False

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
        stat = Statistic.objects.get_or_create(
            user=user,
            quiz=obj,
        )[0]
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
    answer_list = UserAnswerListSerializer(many=True, read_only=True)

    class Meta:
        model = UserAnswer
        fields = [
            'answer',
            'answer_text',
            'answer_list'
        ]


class UserQuestionSerializer(serializers.ModelSerializer):
    answers = UserAnswerSerializer(many=True, read_only=True)
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


class QuestionAdminSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обработки вложенных данных.
    Предназначен для обработки данных на стороне администратора.
    """
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'question_type', 'text', 'image', 'answers']

    def create(self, validated_data):
        answers_data = validated_data.pop('answers', [])
        question = Question.objects.create(**validated_data)
        for answer_data in answers_data:
            answers_list_data = answer_data.pop('answers_list', [])
            # Получаем значение is_right или False, если не передано.
            # Т.к. в моделях это поле необходимо, без такой проверки не
            # получится выполнить POST-запрос. Либо так, либо в модели Answer,
            # поле is_right сделать null=True.
            # В данный момент is_true можем передавать, а можем и не
            # передавать.
            is_right = answer_data.pop('is_right', False)
            answer = Answer.objects.create(
                question=question, is_right=is_right, **answer_data
            )
            for answer_list_data in answers_list_data:
                AnswerList.objects.create(answer=answer, **answer_list_data)
        return question

    def update(self, instance, validated_data):
        answers_data = validated_data.pop('answers', [])
        instance.question_type = validated_data.get('question_type',
                                                    instance.question_type)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        # Обновляем данные ответов
        for answer_data in answers_data:
            answer_id = answer_data.get('id', None)
            if answer_id is None:
                # Если id ответа не передан, значит это новый ответ,
                # создаем его
                answers_list_data = answer_data.pop('answers_list', [])
                is_right = answer_data.pop('is_right', False)
                answer = Answer.objects.create(question=instance,
                                               is_right=is_right,
                                               **answer_data)
                for answer_list_data in answers_list_data:
                    AnswerList.objects.create(answer=answer,
                                              **answer_list_data)
            else:
                # Если id ответа передан, значит это существующий ответ,
                # обновляем его
                try:
                    answer = Answer.objects.get(id=answer_id,
                                                question=instance)
                except Answer.DoesNotExist:
                    continue
                answer.text = answer_data.get('text', answer.text)
                answer.image = answer_data.get('image', answer.image)
                answer.save()

        return instance


class QuizAdminSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с квизами на стороне администратора.
    """
    tags = TagSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ['id', 'image', 'description', 'directory', 'name',
                  'duration', 'level', 'tags', 'threshold']

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        quiz = Quiz.objects.create(**validated_data)

        for tag_data in tags_data:
            tag, _ = Tag.objects.get_or_create(
                name=tag_data['name'], color=tag_data['color']
            )
            quiz.tags.add(tag)

        return quiz

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', [])
        instance.image = validated_data.get('image', instance.image)
        instance.description = validated_data.get('description',
                                                  instance.description)
        instance.directory = validated_data.get('directory',
                                                instance.directory)
        instance.name = validated_data.get('name', instance.name)
        instance.duration = validated_data.get('duration', instance.duration)
        instance.level = validated_data.get('level', instance.level)
        instance.threshold = validated_data.get('threshold',
                                                instance.threshold)
        instance.save()

        # Обновляем данные тегов
        for tag_data in tags_data:
            tag_id = tag_data.get('id', None)
            if tag_id is None:
                continue  # Пропускаем создание новых тегов при обновлении
            else:
                # Если id тега передан, значит это существующий тег,
                # обновляем его
                try:
                    tag = Tag.objects.get(id=tag_id, quiz=instance)
                except Tag.DoesNotExist:
                    continue
                tag.name = tag_data.get('name', tag.name)
                tag.color = tag_data.get('color', tag.color)
                tag.save()

        return instance
