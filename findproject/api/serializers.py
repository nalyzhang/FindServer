from rest_framework import serializers
from django.db.models import Avg

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
    """Сериализатор для модели Route"""

    start = LocationSerializer(read_only=True)
    end = LocationSerializer(read_only=True)
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
    distance = serializers.FloatField()
    time = serializers.TimeField()
    date = serializers.DateField()

    class Meta:
        model = Route
        fields = [
            'id', 'start', 'end', 'start_id', 'finish_id',
            'distance', 'time', 'date'
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

            if start == finish:
                raise serializers.ValidationError(
                    "Начальная и конечная точки не могут совпадать"
                )

        return attrs

    def create(self, validated_data):
        """Создание маршрута"""
        return Route.objects.create(**validated_data)


class UserRouteStatisticSerializer(serializers.Serializer):
    """Сериализатор для статистики пользователя на основе его маршрутов"""

    user = UserSerializer(read_only=True)
    routes = serializers.SerializerMethodField()
    routes_count = serializers.IntegerField(read_only=True)
    average_radius = serializers.FloatField(read_only=True)

    def get_routes(self, obj):
        """Получить маршруты пользователя"""
        if isinstance(obj, User):
            routes = obj.routes.all().select_related('start', 'finish')
            return RouteSerializer(routes, many=True).data
        return []

    def to_representation(self, instance):
        """Преобразование для пользователя"""
        if isinstance(instance, User):
            routes = instance.routes.all()
            routes_count = routes.count()

            avg_radius = routes.filter(
                start__radius__isnull=False
            ).aggregate(
                avg=Avg('start__radius')
            )['avg']

            return {
                'user': UserSerializer(instance, context=self.context).data,
                'routes': RouteSerializer(routes, many=True).data,
                'routes_count': routes_count,
                'average_radius': avg_radius if avg_radius else 0
            }
        return super().to_representation(instance)
