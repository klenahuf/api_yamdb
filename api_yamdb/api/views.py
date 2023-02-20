from smtplib import SMTPResponseException

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Review
from titles.models import Category, Genre, Title
from users.models import User
from users.permissions import IsAdminUser

from .filters import TitleFilter
from .mixins import GetListCreateDeleteMixin
from .permissions import IsAdminModeratorAuthor, IsAdminOrReadOnly
from .serializers import (CategorySerializer, CommentSerializer,
                          CreateTokenSerializer, CreateUserSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleGetSerializer, TitleSerializer, UserSerializer)


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведения."""
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter
    permission_classes = [IsAdminOrReadOnly, ]

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH',):
            return TitleSerializer
        return TitleGetSerializer


class CategoryViewSet(GetListCreateDeleteMixin):
    """Вьюсет для категории."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly, ]
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('name', 'slug',)
    lookup_field = 'slug'


class GenreViewSet(GetListCreateDeleteMixin):
    """Вьюсет для жанра."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly, ]
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('name', 'slug')
    lookup_field = 'slug'


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminModeratorAuthor, ]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(title=title, author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAdminModeratorAuthor, ]

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet модели User."""
    queryset = User.objects.all()
    permission_classes = (IsAdminUser,)
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'username'
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        detail=False,
        methods=(['GET', 'PATCH']),
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        """Получение данных своей учётной записи."""
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data)

        serializer = UserSerializer(
            request.user, data=request.data, partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    """Создание нового пользователя."""
    serializer = CreateUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    email = serializer.validated_data.get('email')
    user, created = User.objects.get_or_create(username=username, email=email)
    token = default_token_generator.make_token(user)

    try:
        send_mail(
            'confirmation code',
            token,
            settings.MAILING_EMAIL,
            [email],
            fail_silently=False,
        )
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    except SMTPResponseException:
        user.delete()
        return Response(
            data={'error': 'Ошибка при отправки кода подтверждения!'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def create_token(request):
    """Создание JWT-токена для пользователей."""
    serializer = CreateTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data.get('username')
    )
    confirmation_code = serializer.validated_data.get('confirmation_code')
    token = default_token_generator.check_token(user, confirmation_code)

    if token == serializer.validated_data.get('confirmation_code'):
        jwt_token = RefreshToken.for_user(user)
        return Response(
            {'token': f'{jwt_token}'}, status=status.HTTP_200_OK
        )
    return Response(
        {'message': 'Отказано в доступе'},
        status=status.HTTP_400_BAD_REQUEST
    )
