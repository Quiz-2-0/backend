from rest_framework import permissions, viewsets, response, status, mixins
from quizes import models, serializers
from django.db.models import Exists, OuterRef


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


class UserAnswerViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = models.UserAnswer.objects.all()
    serializer_class = serializers.UserAnswerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        answer_id = request.data.get('id')
        serializer = self.get_serializer(data={"id": answer_id})
        serializer.is_valid(raise_exception=True)
        data = {
            'user': self.request.user.id,
            'quiz': self.kwargs.get('quiz_id'),
            'answer': answer_id
        }
        save_serializer = serializers.UserAnswerSaveSerializer(data=data)
        save_serializer.is_valid(raise_exception=True)
        self.perform_create(save_serializer)

        return response.Response(status=status.HTTP_201_CREATED)


class StatisticViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.StatisticSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        quiz_id = self.kwargs.get('quiz_id')
        new_queryset = models.UserAnswer.objects.filter(
            user=user,
            quiz__id=quiz_id
        )
        return new_queryset
