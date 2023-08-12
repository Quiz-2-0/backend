from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime
from django.db.models import Sum


User = get_user_model()


class UserLevel(models.Model):
    level = models.PositiveIntegerField(
        verbose_name='Уровень пользователя',
        unique=True
    )
    description = models.CharField(
        verbose_name='Описание уровня',
        max_length=100,
        blank=True
    )
    prev_level = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        related_name='next_level',
        on_delete=models.CASCADE,
        verbose_name='Предыдущий уровень',
    )
    to_level_up = models.PositiveIntegerField(
        verbose_name='Квизов для перехода на следующий уровень',
        default=1
    )
    image = models.ImageField(
        verbose_name='изображение',
        upload_to='user_levels/image/',
        blank=True
    )

    @property
    def not_last_level(self):
        return self.next_level.exists()

    @classmethod
    def get_default(cls):
        obj, _ = cls.objects.get_or_create(level=1)
        return obj.pk

    class Meta:
        verbose_name = 'Уровень пользователя'
        verbose_name_plural = 'Уровени пользователей'
        ordering = ['level']

    def __str__(self):
        return f'Уровень {self.level}, до следующего {self.to_level_up}'


class Rating(models.Model):
    user = models.OneToOneField(
        User,
        related_name='rating',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    count_completed = models.PositiveIntegerField(
        verbose_name='Завершенные квизы',
        default=0
    )
    count_passed = models.PositiveIntegerField(
        verbose_name='Пройденные квизы',
        default=0
    )
    count_assigned = models.PositiveIntegerField(
        verbose_name='Пройденные назначенные квизы',
        default=0
    )
    count_failed = models.PositiveIntegerField(
        verbose_name='Проваленые квизы',
        default=0
    )
    answered_questions = models.PositiveIntegerField(
        verbose_name='Отвеченных вопросов',
        default=0
    )
    right_questions = models.PositiveIntegerField(
        verbose_name='Правильно отвеченных вопросов',
        default=0
    )
    wrong_questions = models.PositiveIntegerField(
        verbose_name='Неверно отвеченных вопросов',
        default=0
    )
    passed_time = models.PositiveIntegerField(
        verbose_name='Время пройденных квизов',
        default=0
    )
    user_rating = models.PositiveIntegerField(
        verbose_name='Рейтинг пользователя',
        default=0
    )

    user_level = models.ForeignKey(
        UserLevel,
        related_name='rating',
        on_delete=models.SET_DEFAULT,
        default=UserLevel.get_default,
        verbose_name='Уровень пользователя',
    )

    @property
    def pass_progress(self):
        return int(
            self.count_passed / (self.user.department.quizes.count() / 100)
        )

    @property
    def to_next_level(self):
        return self.user_level.to_level_up - self.count_passed

    @property
    def in_this_level(self):
        if self.user_level.level != 1:
            return (self.user_level.to_level_up -
                    self.user_level.prev_level.to_level_up)
        return self.user_level.to_level_up

    @property
    def earned_in_level(self):
        if self.user_level.level != 1:
            return (self.count_passed -
                    self.user_level.prev_level.to_level_up)
        return self.count_passed

    @property
    def right_precent(self):
        return int(
            self.right_questions / (self.answered_questions / 100)
        )

    def set_ratings(self):
        statistics = self.user.statistics.all()
        self.count_completed = statistics.filter(is_completed=True).count()
        self.count_passed = statistics.filter(is_passed=True).count()
        self.count_failed = self.count_completed - self.count_passed
        statistics = statistics.filter(is_passed=True)
        self.count_assigned = statistics.filter(is_assigned=True).count()
        statistics = statistics.aggregate(
            count_answered=Sum('count_answered'),
            count_right=Sum('count_right'),
            quiz_time=Sum('quiz_time'),
        )
        self.answered_questions = statistics['count_answered']
        self.right_questions = statistics['count_right']
        self.wrong_questions = self.answered_questions - self.right_questions
        self.passed_time = statistics['quiz_time']
        diff = self.right_questions - self.wrong_questions
        self.user_rating = diff if diff > 0 else 0
        if self.user_level.not_last_level and (
            self.user_level.to_level_up >= self.count_passed
        ):
            self.user_level = self.user_level.next_level.first()
        self.save()
        self.user.achivements.set(Achivement.objects.all())
        for achivement in self.user.user_achivements.all():
            achivement.set_achivement()

    class Meta:
        verbose_name = 'Рейтинг пользователя'
        verbose_name_plural = 'Рейтинги пользователей'
        ordering = ['-user_rating', 'passed_time']

    def __str__(self):
        return f'Рейтинг пользователя {self.user}'


class Achivement(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название достижения',
    )
    description = models.TextField(
        verbose_name='Описание достижения',
    )
    image = models.ImageField(
        verbose_name='изображение',
        upload_to='achivements/image/',
        blank=True
    )
    num_of_completed = models.PositiveIntegerField(
        verbose_name='Завершенных квизов',
        default=0
    )
    num_of_passed = models.PositiveIntegerField(
        verbose_name='Пройденных квизов',
        default=0
    )
    num_of_failed = models.PositiveIntegerField(
        verbose_name='Проваленных квизов',
        default=0
    )
    num_of_assigned = models.PositiveIntegerField(
        verbose_name='Пройденных назначенных квизов',
        default=0
    )
    num_of_questions = models.PositiveIntegerField(
        verbose_name='Отвечено вопросов',
        default=0
    )
    num_of_right_questions = models.PositiveIntegerField(
        verbose_name='Правильно отвеченных вопросов',
        default=0
    )
    num_of_wrong_questions = models.PositiveIntegerField(
        verbose_name='Неверно отвеченных вопросов',
        default=0
    )
    time_in_quizes = models.PositiveIntegerField(
        verbose_name='Время прохождения пройденных квизов (сек)',
        default=0
    )
    level = models.PositiveIntegerField(
        verbose_name='Уровень пользователя',
        default=0
    )

    user = models.ManyToManyField(
        User,
        through='UserAchivement',
        through_fields=('achivement', 'user',),
        related_name='achivements'
    )

    def count_fields(self):
        return (
            self.num_of_completed + self.num_of_assigned + self.num_of_passed +
            self.num_of_failed + self.num_of_questions + self.time_in_quizes +
            self.num_of_wrong_questions + self.num_of_right_questions +
            self.level
        )

    class Meta:
        verbose_name = 'Достижение'
        verbose_name_plural = 'Достижения'

    def __str__(self):
        return f'Достижение {self.name}'


class UserAchivement(models.Model):
    user = models.ForeignKey(
        User,
        related_name='user_achivements',
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )
    achivement = models.ForeignKey(
        Achivement,
        related_name='user_achivements',
        verbose_name='Достижение',
        on_delete=models.CASCADE
    )
    points_to_get = models.PositiveIntegerField(
        default=0,
        verbose_name='Очков для получения',
    )
    points_now = models.PositiveIntegerField(
        default=0,
        verbose_name='Набранно очков',
    )
    achived = models.BooleanField(
        default=False,
        verbose_name='Достижение получено',
    )
    get_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата получения достижения',
    )

    def set_achivement(self):
        if not self.achived:
            self.points_to_get = self.achivement.count_fields()
            self.points_now = min(
                self.user.rating.count_completed,
                self.achivement.num_of_completed
            )
            self.points_now += min(
                self.user.rating.count_passed,
                self.achivement.num_of_passed
            )
            self.points_now += min(
                self.user.rating.count_failed,
                self.achivement.num_of_failed
            )
            self.points_now += min(
                self.user.rating.count_assigned,
                self.achivement.num_of_assigned
            )
            self.points_now += min(
                self.user.rating.answered_questions,
                self.achivement.num_of_questions
            )
            self.points_now += min(
                self.user.rating.right_questions,
                self.achivement.num_of_right_questions
            )
            self.points_now += min(
                self.user.rating.wrong_questions,
                self.achivement.num_of_wrong_questions
            )
            self.points_now += min(
                self.user.rating.passed_time,
                self.achivement.time_in_quizes
            )
            self.points_now += min(
                self.user.rating.user_level.level,
                self.achivement.level
            )
            if self.points_now == self.points_to_get:
                self.achived = True
                self.get_date = datetime.now().date()
            self.save()

    class Meta:
        verbose_name = 'Достижение пользователя'
        verbose_name_plural = 'Достижения пользователей'

    def __str__(self):
        return (f'{self.achivement} пользователя {self.user} '
                f'- {"получена" if self.achived else "в процессе"}')
