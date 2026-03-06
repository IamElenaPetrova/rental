from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Кастомная модель пользователя на базе стандартного AbstractUser.
    Сейчас без дополнительных полей.
    """

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

