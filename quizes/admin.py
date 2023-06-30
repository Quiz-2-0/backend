from django.contrib import admin
from .models import (
    Quiz,
    Answer,
    Question,
    Statistic,
    AssignedQuiz,
    Tag,
    QuizLevel,
)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('name', 'directory')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'isAnswerRight')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz')


@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz')


@admin.register(AssignedQuiz)
class AssignedQuizAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(QuizLevel)
class QuizLevelAdmin(admin.ModelAdmin):
    list_display = ('name',)
