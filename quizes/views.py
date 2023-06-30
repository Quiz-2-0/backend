from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets, response, status
from quizes import models, serializers


class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        directory = self.request.user.department
        queryset = models.Quiz.objects.filter(directory=directory)
        return queryset


class StatisticViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.StatisticSerializer

    def collect_statistic(self, request):
        user_id = self.request.user.id
        quiz_id = request.data.get('id')
        questions = request.data.get('questions')
        answers = models.Answer.objects.filter(question__quiz__id=quiz_id)
        wrong_answers = 0
        for question in questions:
            if answers.filter(
                question__id=question['id'], isAnswerRight=True
            )[0].id != question['answers'][0]['id']:
                wrong_answers += 1
        if models.Statistic.objects.filter(
            user=user_id, quiz=quiz_id
        ).exists():
            statistic = get_object_or_404(
                models.Statistic, user=user_id, quiz=quiz_id
            )
            if statistic.wrong_answers > wrong_answers:
                statistic.wrong_answers = wrong_answers
                statistic.save()
            return response.Response(status=status.HTTP_201_CREATED)
        serializer = serializers.StatisticSerializer(data={
            'user': user_id, 'quiz': quiz_id, 'wrong_answers': wrong_answers
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(status=status.HTTP_201_CREATED)
