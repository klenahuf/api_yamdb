import datetime as dt
from django.db.models import Avg
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from reviews.models import Comment, Review
from titles.models import Category, Genre, Title
from users.models import User
from .validators import validate_email, validate_username


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


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genre
    

class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.SerializerMethodField()
    
    # def create(self, validated_data):
    #     if 'genre' in validated_data:
    #         genre_data = validated_data.pop('genre')
    #         lst = []
    #         for genre in genre_data:
    #             current_genre, status = Genre.objects.get(
    #                 **genre
    #             )
    #             lst.append(current_genre)
    #         instance.genre.set(lst)

    def get_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            rating = reviews.aggregate(Avg('score'))['score__avg']
            rating = round(rating, 2)
        else:
            rating = None
        return rating

    def validate_year(self, year):
        if year > dt.datetime.now().year:
            raise serializers.ValidationError(
                'Год выпуска не может быть больше текущего года')
        return year

    class Meta:
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
        model = Title


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            validate_username
        ],
        required=True,
        max_length=150,
    )
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            validate_email
        ],
        max_length=254,
    )

    class Meta:
        fields = ("username", "email", "first_name",
                  "last_name", "bio", "role")
        model = User
        lookup_field = 'username'


class UserEditSerializer(serializers.ModelSerializer):
    username = serializers.RegexField(regex=r'^[\w.@+-]+$', required=True, max_length=150)

    class Meta:
        fields = ("username", "email", "first_name",
                  "last_name", "bio", "role")
        model = User
        read_only_fields = ('role',)


# class RegisterSerializer(serializers.ModelSerializer):
#     username = serializers.CharField(
#         validators=[
#             UniqueValidator(queryset=User.objects.all()),
#         ],
#         max_length=150,
#     )
#     email = serializers.EmailField(
#         validators=[
#             UniqueValidator(queryset=User.objects.all())
#         ],
#         max_length=254,
#     )

#     def validate_username(self, value):
#         if value.lower() == "me":
#             raise serializers.ValidationError("Username 'me' is not valid")
#         return value

#     class Meta:
#         fields = ("username", "email")
#         model = User


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(
        max_length=254, allow_blank=False, validators=[validate_email]
    )
    username = serializers.CharField(
        max_length=150, allow_blank=False, validators=[validate_username]
    )

    class Meta:
        model = User
        fields = ('email', 'username')
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=['email', 'username']
            )
        ]

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        instance.save()
        return instance


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()
