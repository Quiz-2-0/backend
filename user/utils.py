from django.core.mail import send_mail


def password_mail(email, password):
    """Функция для отправки пароля по электронной почте."""
    send_mail(
        "Авторизационные данные",
        f"Ваш пароль для входа: {password}",
        "corpquiz@yandex.ru",
        [email],
        fail_silently=False,
    )
