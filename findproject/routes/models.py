from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import username_validator


class User(AbstractUser):
    """Кастомная модель пользователя."""

    username = models.CharField(
        'Ник',
        max_length=150,
        unique=True,
        validators=[username_validator],
    )

    email = models.EmailField(
        'Электронная почта', max_length=254, blank=False, unique=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
    )
    last_name = models.CharField(
        'Фамилия', max_length=150,
    )
    avatar = models.ImageField(
        'Аватар', upload_to='users/avatars/',
        null=True, blank=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'last_name', 'first_name', ]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['email']

    def __str__(self):
        return self.username


class Location(models.Model):
    """Локация (точка)"""
    longitude = models.FloatField(
        'Долгота'
    )
    latitude = models.FloatField(
        'Широта'
    )
    radius = models.FloatField(
        'Радиус поиска',
        null=True,
        blank=True
    )
    address = models.CharField(
        'Адрес',
        max_length=250
    )
    time = models.DateTimeField(
        'Время на точке'
    )

    class Meta:
        verbose_name = 'Локация'
        verbose_name_plural = 'Локации'
        ordering = ['time']

    def __str__(self):
        return self.address


class Route(models.Model):
    """
    Маршрут
    Модель для связи двух локаций
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Создатель маршрута',
        related_name='routes'  # Для обратной связи user.routes
    )
    start = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        verbose_name='Стартовая позиция',
        related_name='routes_start'
    )
    finish = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        verbose_name='Конечная позиция',
        related_name='routes_finish'
    )
    stop = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        verbose_name='Позиция остановки',
        related_name='routes_stop',
        null=True,
        blank=True
    )
    distance = models.FloatField(
        'Расстояние'
    )

    @property
    def date(self):
        return self.start.time.date() if self.start else None

    @property
    def time(self):
        if self.start and self.finish:
            delta = self.finish.time - self.start.time
            # Вернуть time объект или timedelta, зависит от вашей логики
            return (datetime.min + delta).time()  # как time
            # или оставить timedelta, сменив тип поля в бизнес-логике
        return None

    class Meta:
        verbose_name = 'Маршрут'
        verbose_name_plural = 'Маршруты'
        ordering = ['start__time']
        unique_together = ['start', 'finish']

    def __str__(self):
        return f'{self.start} - {self.finish}'


class Friend(models.Model):
    """Добавление друзей"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='friends',
        verbose_name='Пользователь'
    )
    friend = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='friend_of',
        verbose_name='Друг'
    )

    class Meta:
        verbose_name = 'Подписка на друга'
        verbose_name_plural = 'Подписки на друзей'
        constraints = [
            models.UniqueConstraint(fields=['user', 'friend'],
                                    name='unique_friend')
        ]
