from django.db import models
from django.contrib.auth import get_user_model
from user.models import Department

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Тег'
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет',
        blank=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class QuizLevel(models.Model):
    name = models.CharField(
        max_length=50, verbose_name='Наименование уровня'
    )
    description = models.CharField(
        max_length=500, verbose_name='Описание уровня'
    )

    class Meta:
        verbose_name = 'Уровень квиза'
        verbose_name_plural = 'уровни квиза'

    def __str__(self):
        return f'{self.name}'


class Quiz(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Наименование квиза'
    )
    description = models.TextField(
        verbose_name='Описание квиза'
    )
    image = models.ImageField(
        verbose_name='изображение',
        upload_to='quizes/image/',
        blank=True
    )
    directory = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        related_name='quizes',
        verbose_name='Направление',
        blank=True,
        null=True
    )
    level = models.ForeignKey(
        QuizLevel,
        on_delete=models.SET_NULL,
        related_name='quizes',
        verbose_name='Уровень квиза',
        blank=True,
        null=True
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='quizes',
        verbose_name='Теги',
        blank=True,
    )
    duration = models.SmallIntegerField(
        verbose_name='Время прохождения в минутах'
    )

    @property
    def question_amount(self):
        return self.questions.count()

    class Meta:
        verbose_name = 'Квиз'
        verbose_name_plural = 'Квизы'

    def __str__(self):
        return f'{self.name}'


class Question(models.Model):
    text = models.TextField(
        verbose_name='Вопрос'
    )
    image = models.ImageField(
        upload_to='questions/image/',
        verbose_name='изображение',
        blank=True
    )
    quiz = models.ForeignKey(
        Quiz,
        related_name='questions',
        on_delete=models.CASCADE,
        verbose_name='Квизы',
    )

    explanation = models.TextField(
        verbose_name='Объяснение',
        blank=True
    )

    @property
    def right_answer(self):
        return self.answers.filter(is_right=True).first().text

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return f'{self.text}'


class Answer(models.Model):
    text = models.CharField(
        max_length=240,
        verbose_name='Текст ответа'
    )
    image = models.ImageField(
        verbose_name='изображение',
        upload_to='answers/image/',
        blank=True
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Вопрос',
    )
    is_right = models.BooleanField(verbose_name='правильный ответ')

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'

    def __str__(self):
        return f'{self.text}'


class AssignedQuiz(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned',
        verbose_name='пользователь'
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='assigned',
        verbose_name='Квиз'
    )

    class Meta:
        verbose_name = 'Назначенный квиз'
        verbose_name_plural = 'Назначенные квизы'

    def __str__(self):
        return f'{self.user.email} - {self.quiz.name}'


class Volume(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.SET_NULL,
        related_name='volumes',
        verbose_name='Квиз',
        blank=True,
        null=True,
    )
    name = models.CharField(
        max_length=500,
        verbose_name='Наименование учебного материала'
    )
    description = models.TextField(
        verbose_name='Описание учебного материала'
    )

    class Meta:
        verbose_name = 'Учебный материал'
        verbose_name_plural = 'Учебные материалы'

    def __str__(self):
        return f'{self.name}'


class UserAnswer(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_answers',
        verbose_name='пользователь'
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='user_answers',
        verbose_name='Квиз'
    )
    answer = models.ForeignKey(
        Answer,
        related_name='user_answers',
        on_delete=models.CASCADE,
        verbose_name='Ответ'
    )

    @property
    def count_questions(self):
        return self.quiz.questions.count()

    class Meta:
        verbose_name = 'Ответ пользователя'
        verbose_name_plural = 'Ответы пользователя'

    def __str__(self):
        return f'{self.user.email} - {self.answer.text} {self.answer.is_right}'
