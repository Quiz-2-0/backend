from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.db.models import Exists, F, OuterRef
from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, permissions, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from quizes import models, serializers

User = get_user_model()


class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для просмотра квизов."""

    serializer_class = serializers.QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает квизы, соответствующие отделу текущего пользователя.

        Каждый квиз аннотирован информацией о том, был ли он назначен пользователю.
        """
        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        directory = self.request.user.department
        user = self.request.user
        new_queryset = (
            models.Quiz.objects.select_related("directory", "level")
            .prefetch_related("tags")
            .filter(directory=directory)
            .annotate(
                appointed=Exists(
                    models.AssignedQuiz.objects.filter(
                        quiz__id=OuterRef("id"), user__id=user.id
                    )
                )
            )
        )
        return new_queryset


# TODO перенести в QuizViewSet
class NotComplitedQuizViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Вьюсет для просмотра незавершенных квизов."""

    serializer_class = serializers.QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Возвращает все незавершенные квизы для текущего пользователя."""
        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        directory = self.request.user.department
        user = self.request.user
        new_queryset = (
            models.Quiz.objects.select_related("directory", "level")
            .prefetch_related("tags")
            .filter(directory=directory)
            .annotate(
                appointed=Exists(
                    models.AssignedQuiz.objects.filter(
                        quiz__id=OuterRef("id"), user__id=user.id
                    )
                )
            )
            .filter(
                statistics__user=user,
                statistics__count_answered__gt=0,
                statistics__count_questions__gt=F("statistics__count_answered"),
            )
        )
        return new_queryset


class UserQuestionViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Вьюсет для создания вопросов пользователя."""

    queryset = models.UserQuestion.objects.all()
    serializer_class = serializers.UserQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Создает новый вопрос пользователя для указанного квиза."""
        quiz = get_object_or_404(models.Quiz, id=self.kwargs.get("quiz_id"))
        statistic, _ = models.Statistic.objects.get_or_create(
            user=self.request.user,
            quiz=quiz,
        )

        data = request.data
        data["statistic"] = statistic.id
        data["question"] = data.get("id")

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        save_serializer = serializers.UserQuestionSaveSerializer(data=data)
        save_serializer.is_valid(raise_exception=True)
        save_serializer.save()

        return Response(status=status.HTTP_201_CREATED)


class QuizLevelViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления уровнями квиза."""

    queryset = models.QuizLevel.objects.all()
    serializer_class = serializers.QuizLevelSerializer
    permission_classes = [permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
        """Создает новый уровень квиза."""
        serializer = serializers.QuizLevelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Обновляет существующий уровень квиза."""
        instance = self.get_object()
        serializer = serializers.QuizLevelSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Удаляет существующий уровень квиза."""
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с тегами со стороны администратора."""

    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer
    permission_classes = [permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
        """Создает новый тег."""
        serializer = serializers.TagSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Обновляет существующий тег."""
        instance = self.get_object()
        serializer = serializers.TagSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Удаляет существующий тег."""
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssignedQuizViewSet(generics.CreateAPIView):
    """Вьюсет для создания назначенных квизов."""

    queryset = models.AssignedQuiz.objects.all()
    serializer_class = serializers.AssignedSerializer
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        """
        Метод для обработки POST-запросов.

        Создает назначенные квизы для указанных пользователей и квизов.
        """
        users = request.data.get("users")
        quizes = request.data.get("quizes")
        for user in users:
            for quiz in quizes:
                # TODO использовать сериализатор для получения объектов
                #  и что-то вроде bulk_update для создания записей
                q = get_object_or_404(models.Quiz, id=quiz["id"])
                u = get_object_or_404(User, id=user["id"])
                _, _ = models.AssignedQuiz.objects.get_or_create(user=u, quiz=q)
        return Response(status=status.HTTP_201_CREATED)


class QuestionAdminViewSet(viewsets.ModelViewSet):
    """Вьюсет для обработки вопросов квизов на стороне администратора."""

    serializer_class = serializers.QuestionAdminSerializer
    permission_classes = [permissions.IsAdminUser]
    # Пустой QuerySet для схемы Swagger.
    queryset = models.Question.objects.none()

    def get_queryset(self):
        """Queryset только для целей схемы Swagger.

        Возвращает QuerySet, который содержит все вопросы квиза.
        """
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        quiz_id = self.kwargs["quiz_id"]
        return models.Question.objects.filter(quiz_id=quiz_id)

    def create(self, request, *args, **kwargs):
        """Создает новые вопросы для указанного квиза."""
        quiz_id = self.kwargs["quiz_id"]
        serializer = serializers.QuestionAdminSerializer(
            data=request.data, context={"quiz_id": quiz_id}
        )
        serializer.is_valid(raise_exception=True)
        created_questions = serializer.save()

        serialized_questions = serializers.QuestionAdminSerializer(
            created_questions, context={"quiz_id": quiz_id}
        ).data

        return Response(serialized_questions, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        """Обновляет существующий вопрос указанного квиза."""
        quiz_id = self.kwargs["quiz_id"]
        question_id = self.kwargs["pk"]
        quiz = get_object_or_404(models.Quiz, pk=quiz_id)
        question = get_object_or_404(models.Question, pk=question_id, quiz=quiz)
        serializer.save(quiz=quiz)

    def perform_destroy(self, instance):
        """Удаляет существующий вопрос указанного квиза."""
        instance.delete()


class QuestionListAdminViewSet(viewsets.ModelViewSet):
    """
    Представление для создания списка вопросов квизов.

    Только для администраторов.
    """

    serializer_class = serializers.QuestionAdminSerializer
    permission_classes = [permissions.IsAdminUser]
    # Пустой QuerySet для схемы Swagger.
    queryset = models.Volume.objects.none()

    def create(self, request, *args, **kwargs):
        """Создает новый список вопросов для указанного квиза."""
        quiz_id = self.kwargs["quiz_id"]
        serializer = serializers.QuestionAdminSerializer(
            data=request.data, many=True, context={"quiz_id": quiz_id}
        )
        serializer.is_valid(raise_exception=True)
        created_questions = serializer.save()

        serialized_questions = serializers.QuestionAdminSerializer(
            created_questions, many=True, context={"quiz_id": quiz_id}
        ).data

        return Response(serialized_questions, status=status.HTTP_201_CREATED)


class QuizAdminViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с квизами со стороны администратора."""

    serializer_class = serializers.QuizAdminSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        """Возвращает квизы с предварительной выборкой тегов."""
        # для оптимизации запросов к БД, чтобы избежать N+1 проблемы,
        # используем prefetch_related вместо all()
        # return models.Quiz.objects.all()
        return models.Quiz.objects.prefetch_related("tags").all()

    def perform_create(self, serializer):
        """Создает новый объект Quiz и добавляет к нему тег, указанный в запросе."""
        tags_data = self.request.data.get("tags", [])
        tag_id = tags_data[0].get("id")
        try:
            # Пытаемся найти тег по id
            tag = models.Tag.objects.get(id=tag_id)
            quiz = serializer.save()
            # Добавляем тег к квизу
            quiz.tags.add(tag)
        except models.Tag.DoesNotExist:
            raise ValidationError("Тег с указанным id не существует.")

    def perform_update(self, serializer):
        """Обновляет объект Quiz и добавляет к нему тег, указанный в запросе."""
        tags_data = self.request.data.get("tags", [])
        tag_id = tags_data[0].get("id")
        try:
            # Пытаемся найти тег по id
            tag = models.Tag.objects.get(id=tag_id)
            quiz = serializer.save()
            # Добавляем тег к квизу
            quiz.tags.add(tag)
        except models.Tag.DoesNotExist:
            raise ValidationError("Тег с указанным id не существует.")

    def perform_destroy(self, instance):
        """Удаляет существующий объект Quiz."""
        instance.delete()


class QuizVolumeViewSet(viewsets.ModelViewSet):
    """
    Представление для работы с учебными материалами определённого квиза.

    Только для администраторов.
    """

    serializer_class = serializers.VolumeSerializer
    permission_classes = [permissions.IsAdminUser]
    # Пустой QuerySet для схемы Swagger.
    queryset = models.Volume.objects.none()

    def get_queryset(self):
        """
        Queryset только для целей схемы Swagger.

        Возвращает QuerySet, который содержит учебные материалы для квиза.
        """
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        quiz_id = self.kwargs["quiz_id"]
        return models.Volume.objects.filter(quiz__id=quiz_id)

    def perform_create(self, serializer):
        """Создает новый объект, связанный с определенным квизом."""
        quiz_id = self.kwargs["quiz_id"]
        quiz = models.Quiz.objects.get(id=quiz_id)
        serializer.save(quiz=quiz)


class StatisticApiView(generics.RetrieveAPIView):
    """Вьюсет для получения статистики по квизу."""

    # TODO сделать сериализатор
    serializer_class = serializers.StatisticSerializer
    queryset = models.Statistic.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Метод для обработки GET-запросов.

        Возвращает статистику по квизу для текущего пользователя.
        """

        def _get_one(user_question, data):
            data["answers"] = []
            for answer in user_question.question.answers.all():
                user_answer = models.UserAnswer.objects.filter(
                    answer=answer, user_question=user_question
                ).first()
                answered = False
                is_right = None
                if user_answer:
                    answered = True
                    is_right = answer.is_right
                data["answers"].append(
                    {
                        "answer_text": answer.text,
                        "answered": answered,
                        "answer_right": is_right,
                        "is_right": answer.is_right,
                    }
                )
            return data

        def _get_lst(user_question, data):
            data["answers"] = []
            for user_answer in user_question.user_answers.all():
                data_answer = {"answer_text": user_answer.answer.text}
                data_answer["answer_list"] = []
                for user_answer_list in user_answer.user_answers_list.all():
                    is_right = (
                        user_answer_list.user_answer.answer
                        == user_answer_list.answer_list.answer
                    )
                    answer_list = {
                        "text": user_answer_list.answer_list.text,
                        "answer_right": is_right,
                    }
                    data_answer["answer_list"].append(answer_list)
                data["answers"].append(data_answer)
            return data

        def _get_opn(user_question, data):
            data["answer"] = user_question.question.answers.first().text
            data["user_answer"] = user_question.user_answers.first().answer_text
            data["is_right"] = user_question.is_right
            return data

        quiz = self.kwargs.get("quiz_id")
        user = request.user
        # TODO запросы с джойнами
        stat = get_object_or_404(models.Statistic, quiz=quiz, user=user)
        data = []
        info = "квиз не пройден"
        if stat.is_completed and not stat.is_passed:
            info = (
                f"Вы ответили правильно менее чем на {stat.quiz.to_passed}" " вопросов"
            )
        if stat.is_passed:
            info = (
                f"Вы ответили правильно на {stat.count_right}"
                f" вопросов из {stat.count_questions}"
            )
            for user_question in stat.user_questions.all():
                question_type = user_question.question.question_type
                question = {
                    "question_type": question_type,
                    "question": user_question.question.text,
                    "explanation": user_question.question.explanation,
                    "is_right": user_question.is_right,
                }
                if question_type in ("ONE", "MNY"):
                    question = _get_one(user_question, question)
                elif question_type == "LST":
                    question = _get_lst(user_question, question)
                elif question_type == "OPN":
                    question = _get_opn(user_question, question)
                else:
                    # TODO подумать над обработкой ошибки
                    continue
                data.append(question)
        result = {"result": stat.is_passed, "info": info, "statistics": data}
        return Response(data=result, status=status.HTTP_200_OK)


class QuizImageViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Представление для просмотра изображений квизов."""

    serializer_class = serializers.QuizImageSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = models.QuizImage.objects.all()


class AssignedAPIView(generics.ListAPIView):
    """Представление для просмотра назначенных квизов."""

    serializer_class = serializers.AssignedSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = models.AssignedQuiz.objects.all()

    def get(self, request, *args, **kwargs):
        """
        Метод для обработки GET-запросов.

        Возвращает список назначенных квизов, сгруппированных по статусу.
        """

        def create_list(queryset, quizes, status):
            for item in queryset:
                if item.quiz.id not in quizes:
                    quizes[item.quiz.id] = {}
                    quizes[item.quiz.id]["name"] = item.quiz.name
                    quizes[item.quiz.id]["department"] = (
                        item.quiz.directory.name if item.quiz.directory else None
                    )
                    quizes[item.quiz.id]["status"] = status
                    quizes[item.quiz.id]["users"] = []
                stat, _ = models.Statistic.objects.get_or_create(
                    user=item.user, quiz=item.quiz
                )
                user = {
                    "id": item.user.id,
                    "name": item.user.full_name,
                    "department": (
                        item.user.department.name if item.user.department else None
                    ),
                    "position": item.user.position,
                    "date": item.pub_date,
                    "is_passed": stat.is_passed,
                }
                quizes[item.quiz.id]["users"].append(user)
            return quizes

        now = datetime.today().date()
        statuses = {"3 дня": 4, "1 неделя": 8, "2 недели": 15, "более 2-х недель": 9999}
        data = {}
        old_value = 0
        for key, value in statuses.items():
            qs = models.AssignedQuiz.objects.filter(
                pub_date__gt=now - timedelta(days=value),
                pub_date__lte=now - timedelta(days=old_value),
            )
            old_value = value
            if qs:
                data[key] = {}
                data[key] = create_list(qs, data[key], key)
        return Response(data=data)


class AssignedQuizUpdateAPIView(generics.CreateAPIView):
    """Вьюсет для обновления назначенных квизов."""

    queryset = models.AssignedQuiz.objects.all()
    serializer_class = serializers.AssignedSerializer
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        """Метод для обработки POST-запросов."""
        users = request.data.get("users")
        quizes = request.data.get("quizes")
        for user in users:
            for quiz in quizes:
                # TODO использовать сериализатор для получения объектов
                #  и что-то вроде bulk_update для создания записей
                q = get_object_or_404(models.Quiz, id=quiz["id"])
                u = get_object_or_404(User, id=user["id"])
                assigned = models.AssignedQuiz.objects.filter(user=u, quiz=q).first()
                if assigned:
                    assigned.save()
        return Response(status=status.HTTP_201_CREATED)


class AssignedQuizDeleteAPIView(generics.CreateAPIView):
    """Вьюсет для удаления назначенных квизов."""

    queryset = models.AssignedQuiz.objects.all()
    serializer_class = serializers.AssignedSerializer
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        """Метод для обработки POST-запросов."""
        users = request.data.get("users")
        quizes = request.data.get("quizes")
        for user in users:
            for quiz in quizes:
                # TODO использовать сериализатор для получения объектов
                #  и что-то вроде bulk_update для создания записей
                q = get_object_or_404(models.Quiz, id=quiz["id"])
                u = get_object_or_404(User, id=user["id"])
                assigned = models.AssignedQuiz.objects.filter(user=u, quiz=q).first()
                if assigned:
                    assigned.delete()
        return Response(status=status.HTTP_201_CREATED)
