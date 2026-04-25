from datetime import datetime, timedelta
from collections import OrderedDict
from rest_framework import serializers
from django.db.models import Count, Avg

from routes.models import User, Location, Route, Friend


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User"""

    is_friend = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'avatar', 'avatar_url', 'is_friend'
        ]
        read_only_fields = ['id', 'is_friend']

    def get_is_friend(self, obj):
        """Проверка, является ли текущий пользователь другом"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Friend.objects.filter(
                user=request.user,
                friend=obj
            ).exists()
        return False

    def get_avatar_url(self, obj):
        """Получить URL аватара"""
        if obj.avatar:
            return obj.avatar.url
        return None


class UserWithStatisticSerializer(UserSerializer):
    """Расширенный сериализатор пользователя со статистикой"""

    routes = serializers.SerializerMethodField()
    routes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['routes', 'routes_count']

    def get_routes(self, obj):
        """Получить маршруты пользователя"""
        routes = obj.routes.all().select_related('start', 'finish')
        return RouteSerializer(routes, many=True, context=self.context).data

    def get_routes_count(self, obj):
        """Количество пройденных маршрутов"""
        return obj.routes.count()


class SetAvatarSerializer(serializers.Serializer):
    """Сериализатор для установки аватара"""

    avatar = serializers.CharField(
        required=True, help_text="Изображение в формате Base64"
    )

    def validate_avatar(self, value):
        """Валидация Base64 изображения"""
        if not value.startswith('data:image/'):
            raise serializers.ValidationError("Неверный формат изображения")
        return value


class UserUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления профиля"""

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def validate_email(self, value):
        """Проверка уникальности email"""
        request = self.context.get('request')
        if request and request.user.email != value:
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError(
                    "Пользователь с таким email уже существует"
                )
        return value

    def validate_username(self, value):
        """Проверка уникальности username"""
        request = self.context.get('request')
        if request and request.user.username != value:
            if User.objects.filter(username=value).exists():
                raise serializers.ValidationError(
                    "Пользователь с таким именем уже существует"
                )
        return value

    def update(self, instance, validated_data):
        """Обновление полей пользователя"""
        instance.username = validated_data.get(
            'username', instance.username)
        instance.email = validated_data.get(
            'email', instance.email)
        instance.first_name = validated_data.get(
            'first_name', instance.first_name)
        instance.last_name = validated_data.get(
            'last_name', instance.last_name)
        instance.save()
        return instance


class SetAvatarResponseSerializer(serializers.Serializer):
    """Сериализатор ответа при установке аватара"""

    avatar = serializers.URLField()


class LocationSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Location"""

    class Meta:
        model = Location
        fields = ['id', 'latitude', 'longitude', 'radius', 'address', 'time']
        read_only_fields = ['id']


class RouteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Route
    Данные для времени и дате формируются на клиенте
    """

    start = LocationSerializer(read_only=True)
    finish = LocationSerializer(read_only=True)
    stop = LocationSerializer(read_only=True)
    start_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        source='start',
        write_only=True
    )
    finish_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        source='finish',
        write_only=True
    )
    stop_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        source='stop',
        write_only=True
    )
    distance = serializers.FloatField()
    time = serializers.TimeField()
    date = serializers.DateField()

    class Meta:
        model = Route
        fields = [
            'id', 'start', 'finish', 'start_id', 'finish_id', 'stop_id',
            'stop', 'distance', 'time', 'date'
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        """Проверка уникальности маршрута"""
        start = attrs.get('start')
        finish = attrs.get('finish')

        if start and finish:
            if Route.objects.filter(start=start, finish=finish).exists():
                raise serializers.ValidationError(
                    "Такой маршрут уже существует"
                )

        return attrs

    def create(self, validated_data):
        """Создание маршрута"""
        return Route.objects.create(**validated_data)


class UserRouteStatisticSerializer(serializers.Serializer):
    """Сериализатор для статистики пользователя на основе его маршрутов"""

    user = UserSerializer(read_only=True)
    routes = serializers.SerializerMethodField()
    routes_count = serializers.SerializerMethodField()
    completed_routes_count = serializers.SerializerMethodField()
    average_radius = serializers.FloatField(read_only=True)

    def __init__(self, *args, **kwargs):
        # Извлекаем параметры фильтрации
        self.date_from = kwargs.pop('date_from', None)
        self.date_to = kwargs.pop('date_to', None)
        super().__init__(*args, **kwargs)

    def get_filtered_routes(self, obj):
        """Получить отфильтрованные по датам маршруты"""
        routes = obj.routes.all()

        if self.date_from:
            routes = routes.filter(date__gte=self.date_from)
        if self.date_to:
            routes = routes.filter(date__lte=self.date_to)

        return routes

    def get_date_range(self):
        """Получить список всех дат в заданном периоде"""
        if not self.date_from or not self.date_to:
            return []

        date_from = datetime.strptime(self.date_from, '%Y-%m-%d').date()
        date_to = datetime.strptime(self.date_to, '%Y-%m-%d').date()

        date_list = []
        current_date = date_from
        while current_date <= date_to:
            date_list.append(current_date.isoformat())
            current_date += timedelta(days=1)

        return date_list

    def get_routes_count(self, obj):
        """Получить массив количества маршрутов по дням"""
        if not isinstance(obj, User):
            return 0

        return self._get_daily_stats(obj, 'all')

    def get_completed_routes_count(self, obj):
        """Получить массив количества завершенных маршрутов по дням"""
        if not isinstance(obj, User):
            return 0

        return self._get_daily_stats(obj, 'completed')

    def _get_daily_stats(self, obj, stat_type):
        """
        Получить статистику по дням

        Args:
            obj: Пользователь
            stat_type: 'all' - все маршруты,
            'completed' - завершенные (stop__isnull=True)
        """
        routes = self.get_filtered_routes(obj)

        if stat_type == 'completed':
            routes = routes.filter(stop__isnull=True)

        # Группируем маршруты по датам и считаем количество
        daily_counts = routes.values('date').annotate(
            count=Count('id')
        ).order_by('date')

        # Преобразуем в словарь для быстрого поиска
        counts_dict = {
            item['date'].isoformat(): item['count']
            for item in daily_counts
        }

        # Если задан период, заполняем все даты
        if self.date_from and self.date_to:
            date_range = self.get_date_range()
            return [counts_dict.get(date, 0) for date in date_range]
        else:
            # Если период не задан, возвращаем общее количество
            return [sum(counts_dict.values())]

    def get_routes(self, obj):
        """Получить маршруты пользователя"""
        if isinstance(obj, User):
            routes = self.get_filtered_routes(obj).select_related(
                'start', 'finish', 'stop')
            return RouteSerializer(routes, many=True).data
        return []

    def to_representation(self, instance):
        """Преобразование для пользователя"""
        if isinstance(instance, User):
            routes = self.get_filtered_routes(instance)

            avg_radius = routes.filter(
                start__radius__isnull=False
            ).aggregate(
                avg=Avg('start__radius')
            )['avg']

            result = OrderedDict()
            result['user'] = UserSerializer(
                instance, context=self.context).data
            result['routes'] = RouteSerializer(routes, many=True).data
            result['routes_count'] = self.get_routes_count(instance)
            result['completed_routes_count'] = self.get_completed_routes_count(
                instance)
            result['average_radius'] = avg_radius if avg_radius else 0

            return result
        return super().to_representation(instance)
