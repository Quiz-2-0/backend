from rest_framework import permissions, viewsets, response, status, mixins
from quizes import models, serializers
from django.db.models import Exists, OuterRef
from rest_framework.decorators import action


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


class AssignedQuizViewSet(viewsets.ModelViewSet):
    queryset = models.AssignedQuiz.objects.all()
    serializer_class = serializers.AssignedSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def create_list(self, request):
        users = request.data.get('users')
        quizes = request.data.get('quizes')
        for user in users:
            for quiz in quizes:
                _, _ = models.AssignedQuiz.objects.get_or_create(
                    user=user, quiz=quiz
                )
        return response.Response(status=status.HTTP_201_CREATED)
