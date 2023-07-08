from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets, response, status
from quizes import models, serializers

class AnswerViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, quiz_id):
        user = self.request.user
        quiz = get_object_or_404(models.Quiz, id=quiz_id)
        answer_id = request.data.get('id')
        answer = get_object_or_404(models.Answer, id=answer_id)

        # Создание записи UserAnswer
        statistic, _ = models.Statistic.objects.get_or_create(user=user, quiz=quiz)
        user_answer = models.UserAnswer.objects.create(statistic=statistic, answer=answer)

        # Обновление статистики в модели Statistic
        statistic.wrong_answers = statistic.user_answers.filter(answer__is_right=False).count()
        statistic.save()

        # Возврат обновленных данных квиза
        queryset = models.Quiz.objects.filter(id=quiz_id)
        serializer = serializers.QuizSerializer(queryset, many=True)

        return response.Response(serializer.data, status=status.HTTP_201_CREATED)

