from rest_framework import filters, viewsets
from django.shortcuts import get_object_or_404
from reviews.models import Review
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from titles.models import Category, Genre, Title
from .filters import TitleFilter
from users.permissions import IsModerOrAdminOrOwnerOrReadOnly, IsAdmin
from .mixins import GetListCreateDeleteMixin
from .serializers import (CategorySerializer, CommentSerializer, GenreSerializer, ReviewSerializer, TitleSerializer)


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
    permission_classes = [IsAdmin, AllowAny,]
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class = TitleFilter

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save()


class CategoryViewSet(GetListCreateDeleteMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin, AllowAny,] 
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class GenreViewSet(GetListCreateDeleteMixin):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdmin, AllowAny]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('slug',)
