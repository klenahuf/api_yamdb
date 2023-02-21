from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from titles.models import Title
from users.models import User

from api_yamdb.settings import NUMBER_OF_SIMBOLS


class Review(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(verbose_name='Дата публикации',
                                    auto_now_add=True)
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1),
                    MaxValueValidator(10)],
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews',
        verbose_name='автор')
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        related_name="reviews", verbose_name='произведение'
    )

    class Meta:
        ordering = ['-pub_date', ]
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            ),
        ]

    def __str__(self):
        return f'{self.title}, {self.score}, {self.author}'


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments',
        verbose_name='автор')
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments',
        verbose_name='отзыв')
    text = models.TextField(
        verbose_name='Текст комментария',
        max_length=200)
    pub_date = models.DateTimeField(verbose_name='Дата добавления',
                                    auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-pub_date', ]
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:NUMBER_OF_SIMBOLS]
