from django.db import models
from django.contrib.auth import get_user_model
from user.models import Department
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

    def create_answer(self, question, answer, time):
        user_question, _ = UserQuestion.objects.get_or_create(
            statistic=self, question=question
        )
        user_question.response_time = time
        if question.question_type == 'ONE':
            update_values = {'answer': answer}
            UserAnswer.objects.update_or_create(
                user_question=user_question,
                defaults=update_values
            )
        elif question.question_type == 'MNY':
            answers = []
            for ans in answer:
                answers.append(
                    UserAnswer(
                        user_question=user_question,
                        answer=ans
                    )
                )
            UserAnswer.objects.filter(user_question=user_question).delete()
            UserAnswer.objects.bulk_create(answers)
        elif question.question_type == 'OPN':
            update_values = {'answer_text': answer}
            UserAnswer.objects.update_or_create(
                user_question=user_question,
                defaults=update_values
            )
        elif question.question_type == 'LST':
            for key, value in answer.items():
                user_answer, _ = UserAnswer.objects.get_or_create(
                    user_question=user_question,
                    answer=key
                )
                answers_list = []
                for ans in value:
                    answers_list.append(
                        UserAnswerList(
                            user_answer=user_answer,
                            answer=ans
                        )
                    )
                UserAnswerList.objects.filter(
                    user_answer=user_answer
                ).delete()
                UserAnswerList.objects.bulk_create(answers_list)

    @property
    def count_answered(self):
        return self.user_questions.count()

    @property
    def count_right(self):
        return self.user_questions.filter(is_right=True).count()

    @property
    def count_wrong(self):
        return self.user_questions.filter(is_right=False).count()

    @property
    def is_passed(self):
        return (self.count_right >= self.quiz.to_passed and
                self.count_answered == self.quiz.question_amount)

    @property
    def quiz_time(self):
        return models.Sum(self.user_questions.response_time)

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

    @property
    def is_answered(self):
        return self.user_answers.exists()

    @property
    def is_right(self):
        question_type = self.question.question_type
        if question_type == 'ONE':
            return self.user_answers.first().answer.is_right
        if question_type == 'MNY':
            return (self.user_answers.filter(answer__is_right=True).count() ==
                    self.question.right_answers)
        if question_type == 'OPN':
            return (self.user_answers.first().answer_text ==
                    self.question.answers.first().text)
        if question_type == 'LST':
            answers = UserAnswerList.objects.filter(
                user_answer__user_question=self
            )
            for answer in answers:
                if answer.answer_list.answer != answer.user_answer.answer:
                    return False
                return True
        return False

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
