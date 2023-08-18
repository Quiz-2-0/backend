from django.core.mail import send_mail
from django.conf import settings


def password_mail(email, password):
    send_mail(
            'Авторизационные данные',
            f'Ваш пароль для входа: {password}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
