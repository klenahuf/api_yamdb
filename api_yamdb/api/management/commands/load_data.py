import csv
from django.core.management.base import BaseCommand
from titles.models import Title, Category, Genre, GenreTitle
from reviews.models import Review, Comment
from users.models import User


class Command(BaseCommand):
    help = 'Import data from CSV files'

    def handle(self, *args, **options):
        with open('static/data/category.csv', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                category = Category(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug']
                )
                category.save()

        with open('static/data/genre.csv', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                genre = Genre(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug']
                )
                genre.save()

        with open('static/data/titles.csv', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                titles = Title(
                    id=row['id'],
                    name=row['name'],
                    year=row['year'],
                    category_id=row['category']
                )
                titles.save()

        with open('static/data/genre_title.csv', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                genre_title = GenreTitle(
                    id=row['id'],
                    title_id=row['title_id'],
                    genre_id=row['genre_id'],
                )
                genre_title.save()

        with open('static/data/users.csv', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                users = User(
                    id=row['id'],
                    username=row['username'],
                    email=row['email'],
                    role=row['role'],
                    bio=row['bio'],
                    first_name=row['first_name'],
                    last_name=row['last_name']
                )
                users.save()

        with open('static/data/review.csv', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                reviews = Review(
                    id=row['id'],
                    title_id=row['title_id'],
                    text=row['text'],
                    author_id=row['author'],
                    score=row['score'],
                    pub_date=row['pub_date']
                )
                reviews.save()

        with open('static/data/comments.csv', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                comments = Comment(
                    id=row['id'],
                    review_id=row['review_id'],
                    text=row['text'],
                    author_id=row['author'],
                    pub_date=row['pub_date']
                )
                comments.save()

        self.stdout.write(self.style.SUCCESS('Data imported successfully'))
