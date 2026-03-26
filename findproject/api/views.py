from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
import base64
import uuid

from routes.models import User, Route, Friend, Location
from .serializers import (
    UserSerializer, UserWithStatisticSerializer,
    SetAvatarSerializer, SetAvatarResponseSerializer, RouteSerializer,
    UserRouteStatisticSerializer, LocationSerializer
)


class UserViewSet(viewsets.GenericViewSet):
    """ViewSet для работы с пользователями"""
    queryset = User.objects.all()

    def get_serializer_class(self):
        return UserSerializer

    def list(self, request):
        """Список пользователей"""
        users = self.get_queryset().exclude(id=request.user.id)

        serializer = self.get_serializer(
            users, many=True, context={'request': request}
        )
        return Response({
            'count': users.count(),
            'results': serializer.data
        })

    def retrieve(self, request, pk=None):
        """Профиль пользователя"""
        user = get_object_or_404(User, id=pk)

        if 'statistic' in request.query_params:
            serializer = UserWithStatisticSerializer(
                user, context={'request': request}
            )
        else:
            serializer = UserSerializer(user, context={'request': request})

        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """Текущий пользователь"""
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def manage_avatar(self, request):
        """
        Управление аватаром пользователя:
        PUT - добавление/обновление, DELETE - удаление
        """

        if request.method == 'PUT':
            serializer = SetAvatarSerializer(data=request.data)
            if serializer.is_valid():
                avatar_data = serializer.validated_data['avatar']

                if request.user.avatar:
                    request.user.avatar.delete()

                format, imgstr = avatar_data.split(';base64,')
                ext = format.split('/')[-1]

                filename = f"{uuid.uuid4()}.{ext}"
                data = ContentFile(base64.b64decode(imgstr), name=filename)
                request.user.avatar.save(filename, data, save=True)

                response_serializer = SetAvatarResponseSerializer({
                    'avatar': request.user.avatar.url
                })
                return Response(
                    response_serializer.data, 
                    status=status.HTTP_200_OK
                )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        elif request.method == 'DELETE':
            # Удаление аватара
            if request.user.avatar:
                request.user.avatar.delete()
                request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    # ==================== ЭНДПОИНТЫ ДРУЗЕЙ ====================

    @action(detail=True, methods=['post', 'delete'], url_path='friend')
    def friend_action(self, request, pk=None):
        """Добавить или удалить друга"""
        friend_user = get_object_or_404(User, id=pk)

        if request.method == 'POST':
            # Добавление друга
            if request.user == friend_user:
                return Response(
                    {"error": "Нельзя добавить самого себя в друзья"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            friendship, created = Friend.objects.get_or_create(
                user=request.user,
                friend=friend_user
            )

            if created:
                serializer = UserWithStatisticSerializer(
                    friend_user, context={'request': request}
                )
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"error": "Пользователь уже в друзьях"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        elif request.method == 'DELETE':
            # Удаление друга
            deleted = Friend.objects.filter(
                user=request.user,
                friend=friend_user
            ).delete()

            if deleted[0]:
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {"error": "Пользователь не в друзьях"},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(detail=False, methods=['get'], url_path='friendslist')
    def friends_list(self, request):
        """Получить список друзей"""
        friends = User.objects.filter(
            friend_of__user=request.user
        ).select_related()

        serializer = UserSerializer(
            friends, many=True, context={'request': request}
        )
        return Response({
            'count': friends.count(),
            'results': serializer.data
        })

    # ==================== ЭНДПОИНТЫ СТАТИСТИКИ ====================

    @action(detail=True, methods=['get'], url_path='statistic')
    def user_statistic(self, request, pk=None):
        """Получить статистику пользователя (его маршруты)"""
        user = get_object_or_404(User, id=pk)
        serializer = UserRouteStatisticSerializer(
            user, context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='me/statistic')
    def my_statistic(self, request):
        """Получить статистику текущего пользователя"""
        serializer = UserRouteStatisticSerializer(
            request.user,
            context={'request': request}
            )
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='statistics')
    def friends_statistics(self, request):
        """Получить статистики всех друзей"""
        friends = User.objects.filter(
            friend_of__user=request.user
        ).prefetch_related('routes__start', 'routes__finish')

        results = []
        for friend in friends:
            routes = friend.routes.all()
            results.append({
                'user': UserSerializer(
                    friend, context={'request': request}
                ).data,
                'routes': RouteSerializer(routes, many=True).data,
                'routes_count': routes.count()
            })

        return Response({
            'count': len(results),
            'results': results
        })


class RouteViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с маршрутами"""
    queryset = Route.objects.all().select_related('start', 'finish')
    serializer_class = RouteSerializer

    def perform_create(self, serializer):
        """При создании маршрута привязываем к текущему пользователю"""
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """Возвращаем только маршруты текущего пользователя"""
        return super().get_queryset().filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """Список маршрутов пользователя"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })

    def create(self, request, *args, **kwargs):
        """Создание маршрута"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """Удаление маршрута"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class LocationViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с локациями (только создание)"""
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    http_method_names = ['post']
