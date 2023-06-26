from django.core.mail import send_mail


def password_mail(email, password):
    send_mail(
            'Авторизационные данные',
            f'Ваш пароль для входа: {password}',
            'ADMIN@example.ru',
            (email,),
            fail_silently=False,
        )
