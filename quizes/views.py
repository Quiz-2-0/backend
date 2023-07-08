from django.shortcuts import get_object_or_404
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
            isPassed=Exists(models.Statistic.objects.filter(
                quiz__id=OuterRef('id'), user__id=user.id
            )),
            appointed=Exists(models.AssignedQuiz.objects.filter(
                quiz__id=OuterRef('id'), user__id=user.id
            ))
        )
        return new_queryset


class AnswerViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, id):
        user = self.request.user
        quiz = get_object_or_404(models.Quiz, id=id)
        answer_id = request.data.get('id')
        answer = get_object_or_404(models.Answer, id=answer_id)

        statistic, _ = models.Statistic.objects.get_or_create(
            user=user, quiz=quiz
        )

        if models.UserAnswer.objects.filter(
            statistic=statistic, answer__question=answer.question
        ).exists():
            user_answer = get_object_or_404(
                models.UserAnswer,
                statistic=statistic,
                answer__question=answer.question
            )
            user_answer.answer = answer
        else:
            user_answer = models.UserAnswer.objects.create(
                statistic=statistic, answer=answer
            )
        user_answer.save()

        return response.Response(status=status.HTTP_201_CREATED)


class StatisticViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.StatisticAnswerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        statistic = models.Statistic.objects.filter(
            user=self.request.user, id=self.kwargs.get('id')
        ).first()
        if statistic is None:
            return response.Response(status=status.HTTP_404_NOT_FOUND)
        new_queryset = models.UserAnswer.objects.filter(statistic=statistic)
        return new_queryset
