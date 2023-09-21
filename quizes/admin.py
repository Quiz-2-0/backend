from django.contrib import admin

from .models import (
    Answer,
    AnswerList,
    AssignedQuiz,
    Question,
    Quiz,
    QuizImage,
    QuizLevel,
    Statistic,
    Tag,
    UserAnswer,
    UserAnswerList,
    UserQuestion,
    Volume,
)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """Добавление модели Quiz в админку."""

    list_display = ("name", "directory")


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """Добавление модели Answer в админку."""

    list_display = ("text", "question", "is_right")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Добавление модели Question в админку."""

    list_display = ("text", "quiz")


@admin.register(AssignedQuiz)
class AssignedQuizAdmin(admin.ModelAdmin):
    """Добавление модели AssignedQuiz в админку."""

    list_display = ("user", "quiz", "pub_date")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Добавление модели Tag в админку."""

    list_display = ("name",)


@admin.register(QuizLevel)
class QuizLevelAdmin(admin.ModelAdmin):
    """Добавление модели QuizLevel в админку."""

    list_display = ("name",)


@admin.register(Volume)
class VolumeAdmin(admin.ModelAdmin):
    """Добавление модели Volume в админку."""

    list_display = ("name", "quiz")


@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    """Добавление модели Statistic в админку."""

    list_display = ("quiz", "user")


@admin.register(UserQuestion)
class UserQuestionAdmin(admin.ModelAdmin):
    """Добавление модели UserQuestion в админку."""

    list_display = ("statistic", "question")


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    """Добавление модели UserAnswer в админку."""

    list_display = ("user_question", "answer", "answer_text")


@admin.register(UserAnswerList)
class UserAnswerListAdmin(admin.ModelAdmin):
    """Добавление модели UserAnswerList в админку."""

    list_display = ("user_answer", "answer_list")


@admin.register(AnswerList)
class AnswerListAdmin(admin.ModelAdmin):
    """Добавление модели AnswerList в админку."""

    list_display = ("answer", "text")


@admin.register(QuizImage)
class QuizImageAdmin(admin.ModelAdmin):
    """Добавление модели QuizImage в админку."""

    list_display = ("id", "description")
