from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator


from titles.models import Category, Genre, Title, GenreTitle


class TitleSerializer(serializers.ModelSerializer):
    
    class Meta:
        fields = '__all__'
        model = Title


class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        fields = '__all__'
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    
    class Meta:
        fields = '__all__'
        model = Genre