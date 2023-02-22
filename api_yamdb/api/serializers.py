from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.models import Avg
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Comment, Review
from titles.models import Category, Genre, Title
from users.models import User
from users.validators import meUsername


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанра."""

    class Meta:
        exclude = ('id',)
        model = Genre


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категории."""

    class Meta:
        exclude = ('id',)
        model = Category


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для произведения."""
    category = serializers.SlugRelatedField(
        required=True, slug_field='slug',
        queryset=Category.objects.all())
    genre = serializers.SlugRelatedField(
        required=True, many=True, slug_field='slug',
        queryset=Genre.objects.all())

    class Meta:
        fields = [
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        ]
        model = Title


class TitleGetSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'description', 'year', 'category', 'genre', 'rating'
        )
        read_only_fields = ('id',)

    def get_rating(self, obj):
        obj = obj.reviews.all().aggregate(rating=Avg('score'))
        return obj['rating']


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )

    def validate(self, data):
        request = self.context['request']
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if request.method == 'POST':
            if Review.objects.filter(
                    title=title,
                    author=request.user).exists():
                raise ValidationError(
                    'Допустимо не более 1 отзыва на произведение')
        return data

    def validate_score(self, score):
        if score < 1 or score > 10:
            raise serializers.ValidationError(
                'Рейтинг произведения должен быть от 1 до 10')
        return score

    class Meta:
        fields = '__all__'
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    review = serializers.ReadOnlyField(
        source='review.id'
    )

    class Meta:
        fields = '__all__'
        model = Comment


class UserSerializer(serializers.ModelSerializer):
    """Serializer модели User."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )


class CreateUserSerializer(serializers.Serializer):
    """Serializer создания нового пользователя."""

    email = serializers.EmailField(max_length=254, required=True,)

    username = serializers.CharField(
        max_length=150, required=True,
        validators=[UnicodeUsernameValidator(), meUsername, ]
    )

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        if (
                User.objects.filter(username=username).exists()
                and User.objects.get(username=username).email != email
        ):
            raise serializers.ValidationError(
                'Пользователь с таким username уже зарегистрирован')
        if (
                User.objects.filter(email=email).exists()
                and User.objects.get(email=email).username != username
        ):
            raise serializers.ValidationError(
                'Указанная почта уже зарегестрирована другим пользователем')
        return data


class CreateTokenSerializer(serializers.Serializer):
    """Serializer создания JWT-токена для пользователей."""
    username = serializers.CharField(max_length=150, required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        fields = ('username', 'token')
