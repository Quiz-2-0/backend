from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets, response, status, mixins, generics
from rest_framework.response import Response

from quizes import models, serializers
from django.db.models import Exists, OuterRef
from django.contrib.auth import get_user_model

User = get_user_model()


class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return response.Response(status=status.HTTP_401_UNAUTHORIZED)
        directory = self.request.user.department
        user = self.request.user
        new_queryset = models.Quiz.objects.select_related(
            'directory', 'level'
        ).prefetch_related('tags').filter(
            directory=directory
        ).annotate(
            appointed=Exists(models.AssignedQuiz.objects.filter(
                quiz__id=OuterRef('id'), user__id=user.id
            ))
        )
        return new_queryset


class UserQuestionViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = models.UserQuestion.objects.all()
    serializer_class = serializers.UserQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        statistic = models.Statistic.objects.get_or_create(
            user=self.request.user.id,
            quiz=self.kwargs.get('quiz_id'),
        )[0]

        data = request.data
        data['statistic'] = statistic.id
        data['question'] = data.get('id')

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        save_serializer = serializers.UserQuestionSaveSerializer(data=data)
        save_serializer.is_valid(raise_exception=True)
        save_serializer.save()

        return response.Response(status=status.HTTP_201_CREATED)


class QuizLevelViewSet(viewsets.ModelViewSet):
    queryset = models.QuizLevel.objects.all()
    serializer_class = serializers.QuizLevelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = serializers.QuizLevelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data,
                                 status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = serializers.QuizLevelSerializer(instance,
                                                     data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ModelViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = serializers.TagSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data,
                                 status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = serializers.TagSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class AssignedQuizViewSet(generics.CreateAPIView):
    queryset = models.AssignedQuiz.objects.all()
    serializer_class = serializers.AssignedSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        users = request.data.get('users')
        quizes = request.data.get('quizes')
        for user in users:
            for quiz in quizes:
                q = get_object_or_404(models.Quiz, id=quiz['id'])
                u = get_object_or_404(User, id=user['id'])
                _, _ = models.AssignedQuiz.objects.get_or_create(
                    user=u, quiz=q
                )
        return response.Response(status=status.HTTP_201_CREATED)


class QuestionAdminViewSet(viewsets.ModelViewSet):
    """
    Представление для обработки вопросов квизов на стороне администратора.
    """
    serializer_class = serializers.QuestionAdminSerializer
    permission_classes = [permissions.IsAuthenticated]
    # Пустой QuerySet для схемы Swagger.
    queryset = models.Question.objects.none()

    def get_queryset(self):
        # queryset только для целей схемы Swagger.
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset
        quiz_id = self.kwargs['quiz_id']
        return models.Question.objects.filter(quiz_id=quiz_id)

    def create(self, request, *args, **kwargs):
        quiz_id = self.kwargs['quiz_id']
        serializer = serializers.QuestionAdminSerializer(
            data=request.data, context={'quiz_id': quiz_id}
        )
        serializer.is_valid(raise_exception=True)
        created_questions = serializer.save()

        serialized_questions = serializers.QuestionAdminSerializer(
            created_questions, context={'quiz_id': quiz_id}
        ).data

        return Response(serialized_questions, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        quiz_id = self.kwargs['quiz_id']
        question_id = self.kwargs['pk']
        quiz = get_object_or_404(models.Quiz, pk=quiz_id)
        question = get_object_or_404(models.Question, pk=question_id,
                                     quiz=quiz)
        serializer.save(quiz=quiz)

    def perform_destroy(self, instance):
        instance.delete()


class QuestionListAdminViewSet(viewsets.ModelViewSet):
    """
    Представление для создания списка вопросов квизов на стороне
    администратора.
    """
    serializer_class = serializers.QuestionAdminSerializer
    permission_classes = [permissions.IsAuthenticated]
    # Пустой QuerySet для схемы Swagger.
    queryset = models.Volume.objects.none()

    def create(self, request, *args, **kwargs):
        quiz_id = self.kwargs['quiz_id']
        serializer = serializers.QuestionAdminSerializer(
            data=request.data, many=True, context={'quiz_id': quiz_id}
        )
        serializer.is_valid(raise_exception=True)
        created_questions = serializer.save()

        serialized_questions = serializers.QuestionAdminSerializer(
            created_questions, many=True, context={'quiz_id': quiz_id}
        ).data

        return Response(serialized_questions, status=status.HTTP_201_CREATED)


class QuizAdminViewSet(viewsets.ModelViewSet):
    """
    Представление для работы с квизами со стороны администратора.
    """
    serializer_class = serializers.QuizAdminSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # для оптимизации запросов к БД, чтобы избежать N+1 проблемы,
        # используем prefetch_related вместо all()
        # return models.Quiz.objects.all()
        return models.Quiz.objects.prefetch_related('tags').all()

    def perform_create(self, serializer):
        quiz = serializer.save()
        tags_data = self.request.data.get('tags', [])
        tag_ids = [tag_data.get('id') for tag_data in tags_data]
        quiz.tags.set(tag_ids)

    def perform_update(self, serializer):
        quiz = serializer.save()
        tags_data = self.request.data.get('tags', [])
        tag_ids = [tag_data.get('id') for tag_data in tags_data]
        quiz.tags.set(tag_ids)

    def perform_destroy(self, instance):
        instance.delete()


class QuizVolumeViewSet(viewsets.ModelViewSet):
    """
    Представление для работы с учебными материалами определённого квиза
    со стороны администратора.
    """
    serializer_class = serializers.VolumeSerializer
    permission_classes = [permissions.IsAuthenticated]
    # Пустой QuerySet для схемы Swagger.
    queryset = models.Volume.objects.none()

    def get_queryset(self):
        # queryset только для целей схемы Swagger.
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset
        quiz_id = self.kwargs['quiz_id']
        return models.Volume.objects.filter(quiz__id=quiz_id)

    def perform_create(self, serializer):
        quiz_id = self.kwargs['quiz_id']
        quiz = models.Quiz.objects.get(id=quiz_id)
        serializer.save(quiz=quiz)
