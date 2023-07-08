from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets, response, status
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

        # Создание записи UserAnswer
        statistic, _ = models.Statistic.objects.get_or_create(user=user,
                                                              quiz=quiz)
        user_answer = models.UserAnswer.objects.create(statistic=statistic,
                                                       answer=answer)

        # Обновление статистики в модели Statistic
        statistic.wrong_answers = statistic.user_answers.filter(
            answer__is_right=False).count()
        statistic.save()

        # Подготовка данных для ответа
        response_data = {
            'id': id,
            'currentUserAnswer': answer_id,
            'amountOfRightAnswers': statistic.count_questions - statistic.wrong_answers,
            'progressOfAnswers': user_answer.id
        }

        return response.Response(response_data, status=status.HTTP_201_CREATED)


class StatisticViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, id):
        statistic = models.Statistic.objects.filter(
            user=request.user, id=id
        ).first()
        if statistic is None:
            return response.Response(status=status.HTTP_404_NOT_FOUND)
        user_answers = models.UserAnswer.objects.filter(statistic=statistic)
        data = []
        for user_answer in user_answers:
            question = user_answer.answer.question
            is_right = user_answer.answer.is_right
            explanation = user_answer.answer.explanation if not is_right else None
            data.append({
                'question': question.text,
                'answer': user_answer.answer.text,
                'isRight': is_right,
                'explanation': explanation
            })
        return response.Response(data)


class LastQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.LastQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return models.LastQuestion.objects.filter(statistic__user=user)

    def perform_create(self, serializer):
        user = self.request.user
        statistic_id = self.request.data.get('statistic_id')
        statistic = models.Statistic.objects.get(id=statistic_id, user=user)
        serializer.save(statistic=statistic)
