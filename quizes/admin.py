from django.contrib import admin
from .models import (
    Quiz,
    Answer,
    Question,
    AssignedQuiz,
    Tag,
    QuizLevel,
    Volume,
    Statistic,
    UserQuestion,
    UserAnswer,
    UserAnswerList,
    AnswerList
)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('name', 'directory')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_right')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz')


@admin.register(AssignedQuiz)
class AssignedQuizAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(QuizLevel)
class QuizLevelAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Volume)
class VolumeAdmin(admin.ModelAdmin):
    list_display = ('name', 'quiz')


@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'user')


@admin.register(UserQuestion)
class UserQuestionAdmin(admin.ModelAdmin):
    list_display = ('statistic', 'question')


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('user_question', 'answer', 'answer_text')


@admin.register(UserAnswerList)
class UserAnswerListAdmin(admin.ModelAdmin):
    list_display = ('user_answer', 'answer_list')


@admin.register(AnswerList)
class AnswerListAdmin(admin.ModelAdmin):
    list_display = ('answer', 'text')
