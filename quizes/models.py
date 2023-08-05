from django.db import models
from django.contrib.auth import get_user_model
from user.models import Department
from ratings.models import Rating
from django.core.validators import MaxValueValidator, MinValueValidator

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
    threshold = models.PositiveSmallIntegerField(
        verbose_name='Порог прохождения квиза в %',
        default=70,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )

    @property
    def question_amount(self):
        return self.questions.count()

    @property
    def to_passed(self):
        return int(self.question_amount / 100 * self.threshold)

    class Meta:
        verbose_name = 'Квиз'
        verbose_name_plural = 'Квизы'

    def __str__(self):
        return f'{self.name}'


class Question(models.Model):

    class TypeChoices(models.TextChoices):
        ONE = 'ONE', 'один ответ'
        MANY = 'MNY', 'нексколько ответов'
        LIST = 'LST', 'список ответов'
        OPEN = 'OPN', 'открытый ответ'

    question_type = models.CharField(
        verbose_name='Тип вопроса',
        max_length=3,
        choices=TypeChoices.choices,
        default=TypeChoices.ONE
    )
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

    @property
    def right_answers(self):
        return self.answers.filter(is_right=True).count()

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


class AnswerList(models.Model):
    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name='answers_list',
        verbose_name='ОТвет из списка',
    )
    text = models.CharField(
        max_length=240,
        verbose_name='Текст ответа'
    )

    class Meta:
        verbose_name = 'Ответ из списка'
        verbose_name_plural = 'Ответы из списка'

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


class Statistic(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='statistics',
        verbose_name='пользователь'
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='statistics',
        verbose_name='Квиз'
    )

    count_questions = models.PositiveSmallIntegerField(
        verbose_name='Вопросов в квизе',
        blank=True,
        null=True
    )

    count_answered = models.PositiveSmallIntegerField(
        verbose_name='Вопросов отвечено',
        blank=True,
        null=True
    )

    count_right = models.PositiveSmallIntegerField(
        verbose_name='Правильно вопросов отвечено',
        blank=True,
        null=True
    )

    count_wrong = models.PositiveSmallIntegerField(
        verbose_name='Неверно вопросов отвечено',
        blank=True,
        null=True
    )

    quiz_time = models.PositiveIntegerField(
        verbose_name='Время прохождения квиза',
        blank=True,
        null=True
    )

    is_completed = models.BooleanField(
        verbose_name='Квиз завершен',
        default=False
    )

    is_passed = models.BooleanField(
        verbose_name='Квиз пройден',
        default=False
    )

    is_failed = models.BooleanField(
        verbose_name='Квиз провален',
        default=False
    )

    is_assigned = models.BooleanField(
        verbose_name='Квиз назначен',
        default=False
    )

    mod_date = models.DateField(
        verbose_name='Дата изменения',
        auto_now=True
    )

    @property
    def set_statistic(self):
        self.count_questions = self.quiz.question_amount
        to_passed = self.quiz.to_passed
        self.count_answered = self.user_questions.count()
        self.count_right = self.user_questions.filter(is_right=True).count()
        self.count_wrong = self.count_answered - self.count_right
        self.is_completed = self.count_answered == self.count_questions
        self.is_passed = (
            self.count_right >= to_passed and
            self.is_completed
        )
        self.is_failed = (
            self.count_right < to_passed and
            self.is_completed
        )
        self.is_assigned = AssignedQuiz.objects.filter(
            user=self.user, quiz=self.quiz
        ).exists()
        quiz_time = self.user_questions.aggregate(
            quiz_time=models.Sum('response_time')
        )
        self.quiz_time = quiz_time['quiz_time']
        self.save()
        if self.is_completed:
            rating, _ = Rating.objects.get_or_create(user=self.user)
            rating.set_ratings()

    class Meta:
        verbose_name = 'Статистика прохождения квиза'
        verbose_name_plural = 'Статистика прохождения квизов'

    def __str__(self):
        return f'{self.user} {self.quiz}'


class UserQuestion(models.Model):
    statistic = models.ForeignKey(
        Statistic,
        on_delete=models.CASCADE,
        related_name='user_questions',
        verbose_name='Статистика квиза'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='user_questions',
        verbose_name='Вопрос'
    )
    response_time = models.PositiveIntegerField(
        verbose_name='Время ответа'
    )

    is_right = models.BooleanField(
        verbose_name='Отвечен верно',
        default=False
    )

    @property
    def set_is_right(self):
        def _set_is_right(question_type):
            if question_type == 'ONE':
                return self.user_answers.first().answer.is_right
            if question_type == 'MNY':
                return (
                    self.user_answers.filter(answer__is_right=True).count() ==
                    self.question.right_answers
                )
            if question_type == 'OPN':
                return (self.user_answers.first().answer_text ==
                        self.question.answers.first().text)
            if question_type == 'LST':
                answers = self.user_answers.objects.all()
                for answer in answers:
                    if answer.answer_list.answer != answer.user_answer.answer:
                        return False
                return True
            return False
        question_type = self.question.question_type
        self.is_right = _set_is_right(question_type)
        self.save()
        self.statistic.set_statistic

    class Meta:
        verbose_name = 'Вопрос пользователя'
        verbose_name_plural = 'Вопросы пользователя'

    def __str__(self):
        return f'{self.statistic} {self.question}'


class UserAnswer(models.Model):
    user_question = models.ForeignKey(
        UserQuestion,
        on_delete=models.CASCADE,
        related_name='user_answers',
        verbose_name='Вопрос'
    )
    answer = models.ForeignKey(
        Answer,
        related_name='user_answers',
        on_delete=models.CASCADE,
        verbose_name='Ответ',
        blank=True
    )
    answer_text = models.CharField(
        max_length=240,
        verbose_name='Текст ответа',
        blank=True
    )

    class Meta:
        verbose_name = 'Ответ пользователя'
        verbose_name_plural = 'Ответы пользователя'

    def __str__(self):
        return f'{self.user_question} {self.answer}'


class UserAnswerList(models.Model):
    user_answer = models.ForeignKey(
        UserAnswer,
        related_name='user_answers_list',
        on_delete=models.CASCADE,
        verbose_name='Ответ пользователя'
    )
    answer_list = models.ForeignKey(
        AnswerList,
        related_name='user_answers_list',
        on_delete=models.CASCADE,
        verbose_name='Ответ из списка'
    )

    class Meta:
        verbose_name = 'Ответ пользователя из списка'
        verbose_name_plural = 'Ответы пользователя из списка'

    def __str__(self):
        return f'{self.user_answer} {self.answer_list}'
