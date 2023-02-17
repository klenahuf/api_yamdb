from rest_framework import filters, viewsets, permissions, status
from django.shortcuts import get_object_or_404
from reviews.models import Review
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes

from titles.models import Category, Genre, Title
from .filters import TitleFilter
from users.models import User
from users.permissions import IsModerOrAdminOrOwnerOrReadOnly, IsAdmin
from .mixins import GetListCreateDeleteMixin
from .serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer,
    ReviewSerializer, TitleSerializer, TokenSerializer,
    TokenSerializer, UserEditSerializer, UserSerializer, SignUpSerializer
)
from .permissions import ReadOnly
from rest_framework import status


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsModerOrAdminOrOwnerOrReadOnly, ]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(title=title, author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsModerOrAdminOrOwnerOrReadOnly, ]

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = [IsAdmin | AllowAny]
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class = TitleFilter

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save()


class CategoryViewSet(GetListCreateDeleteMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin | ReadOnly]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(GetListCreateDeleteMixin):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdmin | ReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def get_jwt_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data["username"]
    )

    if default_token_generator.check_token(
        user, serializer.validated_data["confirmation_code"]
    ):
        token = AccessToken.for_user(user)
        return Response({"token": str(token)}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = SignUpSerializer(data=request.data)
    if User.objects.filter(
        username=request.data.get('username'), email=request.data.get('email')
    ).exists():
        user, created = User.objects.get_or_create(
            username=request.data.get('username')
        )
        if created is False:
            confirmation_code = default_token_generator.make_token(user)
            user.confirmation_code = confirmation_code
            user.save()
            return Response(f'Token updated: {confirmation_code}', status=status.HTTP_200_OK)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    user = User.objects.get(
        username=request.data['username'],
        email=request.data['email']
    )
    confirmation_code = default_token_generator.make_token(user)
    user.confirmation_code = confirmation_code
    send_mail(
        'Confirmation code',
        message=f"Confirmation code, {confirmation_code}",
        from_email='yamdb@gmail.com',
        recipient_list=[request.data['email']],
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    lookup_field = "username"
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = ('get', 'post', 'patch', 'delete')

    @action(
        methods=[
            "GET",
            "PATCH",
        ],
        detail=False,
        url_path="me",
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=UserEditSerializer,
    )
    def users_own_profile(self, request):
        user = request.user
        if request.method == "GET":
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == "PATCH":
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
