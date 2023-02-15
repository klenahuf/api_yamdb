from django.db import models


class Category(models.Model):
    """Категории (типы) произведений («Фильмы», «Книги», «Музыка»).
    Одно произведение может быть привязано только к одной категории."""
    name = models.CharField(max_length=200, verbose_name='Категория')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Жанры произведений. Одно произведение может быть
    привязано к нескольким жанрам."""
    name = models.CharField(max_length=200, verbose_name='Жанр')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    """Произведения, к которым пишут отзывы: определённый фильм,
    книга или песенка."""
    name = models.CharField(
        max_length=200, verbose_name='Произведение'
    )
    year = models.IntegerField(verbose_name='Год выпуска')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True,
        related_name='titles'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.title} {self.genre}'
