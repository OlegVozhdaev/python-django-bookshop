from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import IntegrityError
from django.db.models import Count, Q, CharField, Value, OuterRef, Subquery, Exists, Prefetch
from django.db.models.functions import Cast
from django.http import HttpResponse
from django.shortcuts import render, redirect
from managebook.models import BookLike, Book, CommentLike, Comment
from django.views import View
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from managebook.forms import BookForm, CommentForm
from pytils.translit import slugify
from datetime import datetime
from managebook.forms import CustomUserCreateForm, CustomAuthenticationForm
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator


class BookView(View):
   # @method_decorator(cache_page(2))
    def get(self, request):
        # if request.user.username in cache:
        #     result = cache.get(request.user.username)
        #     response = {"content": result, "form": CommentForm()}
        #     return render(request, "index.html", response)
        response = {"form": CommentForm()}
        if request.user.is_authenticated:
            sub_query_1 = BookLike.objects.filter(user=request.user, book=OuterRef('pk')).values('rate')
            sub_query_2 = Exists(User.objects.filter(id=request.user.id, book=OuterRef('pk')))
            sub_query_3 = Exists(User.objects.filter(id=request.user.id, comment=OuterRef('pk')))
            comment = Comment.objects.annotate(is_owner=sub_query_3).select_related('user').prefetch_related('like')
            comment_prefetch = Prefetch('comment', comment)
            result = Book.objects.annotate(user_rate=Cast(sub_query_1, CharField()),
                                           is_owner=sub_query_2) \
                .prefetch_related(comment_prefetch, "author", "genre")
        else:
            result = Book.objects \
                .prefetch_related("author", "genre", "comment", "comment__user").all()
        response["content"] = result
        # cache.set(request.user.username, result, 2)
        return render(request, "index.html", response)


class AddRateBook(View):
    def get(self, request, rate, book_id):
        if request.user.is_authenticated:
            BookLike.objects.create(book_id=book_id, rate=rate, user_id=request.user.id)
        return redirect("hello")


class AddLike(View):
    def get(self, request, comment_id):
        if request.user.is_authenticated:
            CommentLike.objects.create(comment_id=comment_id, user_id=request.user.id)
        return redirect("hello")


class RegisterView(View):
    def get(self, request):
        form = CustomUserCreateForm()
        return render(request, "register.html", {"form": form})

    def post(self, request):
        form = CustomUserCreateForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("hello")
        messages.error(request, "This username is already taken:(")
        return redirect("register")


class LoginView(View):
    def get(self, request):
        form = CustomAuthenticationForm()
        return render(request, "login.html", {"form": form})

    def post(self, request):
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("hello")
        messages.error(request, message="User with this username and password does not exist")
        return redirect("login")


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("hello")


class AddNewBook(View):
    def get(self, request):
        form = BookForm()
        return render(request, "create_book.html", {"form": form})

    def post(self, request):
        book = BookForm(data=request.POST)
        if book.is_valid():
            print("Valid form")
            nb = book.save(commit=False)
            nb.slug = slugify(nb.title)
            try:
                nb.save()
            except IntegrityError:
                nb.slug += datetime.now().strftime("%Y:%m:%d:%H:%M:%S:%f")
                nb.save()
            nb.author.add(request.user)
            book.save_m2m()
            return redirect("hello")
        print("Invalid form")
        return redirect("add_book")


class DeleteBook(View):
    def get(self, request, book_id):
        if request.user.is_authenticated:
            book = Book.objects.get(id=book_id)
            if request.user in book.author.all():
                book.delete()
            return redirect("hello")


class UpdateBook(View):
    def get(self, request, book_slug): #checks premission
        if request.user.is_authenticated:
            book = Book.objects.get(slug=book_slug)
            if request.user in book.author.all():
                bf = BookForm(instance=book)
                return render(request, "update_book.html", {"form": bf, "slug": book.slug})
        return redirect("hello")

    def post(self, request, book_slug): #actual update. vulnerable to custom post request
        book = Book.objects.get(slug=book_slug)
        bf = BookForm(instance=book, data=request.POST)
        if bf.is_valid():
            bf.save()
        return redirect("hello")


class AddComment(View):
    def post(self, request, book_id):
        if request.user.is_authenticated:
            cf = CommentForm(data=request.POST)
            comment = cf.save(commit=False)
            comment.user = request.user
            comment.book_id = book_id
            comment.save()
        return redirect("hello")


class DeleteComment(View):
    def get(self, request, comment_id):
        if request.user.is_authenticated:
            try:
                Comment.objects.get(id=comment_id, user=request.user).delete()
            except Comment.DoesNotExist:
                pass
        return redirect("hello")


class UpdateComment(View):
    def get(self, request, comment_id):
        if request.user.is_authenticated:
            comment = Comment.objects.get(id=comment_id)
            if comment.user == request.user:
                cf = CommentForm(instance=comment)
                return render(request, 'update_comment.html', {'form': cf, 'id': comment.id})
        return redirect("hello")

    def post(self, request, comment_id):
        comment = Comment.objects.get(id=comment_id)
        cf = CommentForm(isinstance=comment, data=request.POST)
        if cf.is_valid():
            cf.save()
        return redirect("hello")

