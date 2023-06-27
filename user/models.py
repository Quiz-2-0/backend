from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model


class Department(models.Model):
    name = models.CharField(
        _("department name"),
        max_length=150
    )


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    first_name = None
    last_name = None

    class UserRoleChoice(models.TextChoices):
        ADMIN = 'AD', _('Admin')
        EMPLOYEE = 'EMP', _('Employee')

    email = models.EmailField(
        max_length=254,
        unique=True
    )
    role = models.CharField(
        _("role"),
        max_length=5,
        choices=UserRoleChoice.choices,
        default=UserRoleChoice.EMPLOYEE
    )
    department = models.ForeignKey(
        Department,
        related_name='departament',
        on_delete=models.SET_NULL,
        verbose_name=_("department"),
        blank=True,
        null=True
    )
    avatar = models.ImageField(
        _("avatar"),
        upload_to='user/avatar/',
        default=None,
        null=True
    )
    firstName = models.CharField(_("first name"), max_length=150)
    lastName = models.CharField(_("last name"), max_length=150)
    patronymic = models.CharField(
        _("patronymic"), max_length=150, blank=True
    )
    position = models.CharField(_("position"), max_length=150)
    score = models.PositiveSmallIntegerField(help_text=_("score"), null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'firstName', 'lastName', 'position', 'role'
    )

    objects = CustomUserManager()

    def __str__(self):
        return (
            f'{self.firstName} {self.lastName[0]}.'
            f'{self.patronymic[0]+"."  if self.patronymic else ""}'
        )

    @property
    def is_admin(self):
        return self.role == self.UserRoleChoice.ADMIN or self.is_superuser


User = get_user_model()
