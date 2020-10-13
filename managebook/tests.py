from django.db import transaction
from django.db.models import Avg
from django.test import TestCase
from django.urls import reverse
from managebook.models import Book, BookLike, Comment, Genre
from django.contrib.auth.models  import User

# Create your tests here.


class TestModel(TestCase):
    def test_rate(self):
        user_1 = User.objects.create(username="user_1")
        user_2 = User.objects.create(username="user_2")
        book = Book.objects.create(text="text", slug="slug")
        BookLike.objects.create(book=book, user=user_1, rate=4)
        BookLike.objects.create(book=book, user=user_2, rate=6)
        rate__avg = book.book_like.aggregate(Avg("rate"))["rate__avg"]
        self.assertEqual(rate__avg, 5)

    def test_cached_rate(self):
        user_1 = User.objects.create(username="user_1")
        user_2 = User.objects.create(username="user_2")
        book = Book.objects.create(text="text", slug="slug")
        BookLike.objects.create(book=book, user=user_1, rate=4)
        BookLike.objects.create(book=book, user=user_2, rate=6)
        self.assertEqual(book.cached_rate, 5)

    def test_comment_like(self):
        user_1 = User.objects.create(username="user_1")
        user_2 = User.objects.create(username="user_2")
        book = Book.objects.create(text="text", slug="slug")
        comment = Comment.objects.create(text="text", user=user_1, book=book)
        comment.like.add(user_2)
        comment.like.add(user_1)
        comment.save()
        likes = comment.like.count()
        self.assertEqual(likes, 2)


class TestViews(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="Test Name", password="test pwd")
        self.client.force_login(self.user)

    def test_hello(self):
        url = reverse('hello')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_add_rate(self):
        book = Book.objects.create(text="text", slug="slug")
        url = reverse('add_rate', args=[7, book.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        book.refresh_from_db()
        self.assertEqual(book.cached_rate, 7)
        self.client.logout()
        url = reverse('add_rate', args=[1, book.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        book.refresh_from_db()
        self.assertEqual(book.cached_rate, 7)

    def test_add_like2comment(self):
        book = Book.objects.create(text="text", slug="slug")
        comment = Comment.objects.create(text="text", user=self.user, book=book)
        url = reverse('add_like2comment', args=[comment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        comment.refresh_from_db()
        self.assertEqual(comment.cached_like, 1)

    def test_add_comment(self):
        book = Book.objects.create(text="text", slug="slug")
        url = reverse('add_comment', args=[book.id])
        data = {'text': 'test_comment_text'}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        book.refresh_from_db()
        self.assertEqual(book.comment.first().text, data['text'])

    def test_delete_book(self):
        book = Book.objects.create(text="text", slug="slug")
        book.author.add(self.user)
        book.save()
        url = reverse('delete_book', args=[book.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Book.objects.count(), 0)

    def test_update_book(self):
        g1 = Genre.objects.create(title='genre_1')
        g2 = Genre.objects.create(title='genre_2')
        book = Book.objects.create(text="text", slug="slug")
        book.author.add(self.user)
        book.genre.add(g1)
        book.save()
        url = reverse('update_book', args=[book.slug])
        data = {'title': 'update new title',
                'text': 'update new text',
                'genre': ['2']}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        book.refresh_from_db()
        self.assertEqual(book.title, data['title'])
        self.assertEqual(book.text, data['text'])
        self.assertEqual(book.genre.first().title, g2.title)

    # def test_two_rate(self):
    #     user_1 = User.objects.create(username="user_1")
    #     book = Book.objects.create(text="text", slug="slug")
    #     BookLike.objects.create(book=book, user=user_1, rate=4)
    #     BookLike.objects.create(book=book, user=user_1, rate=6)

    # coverage run - -source = '.' manage.py test.

