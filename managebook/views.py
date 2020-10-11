from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render, redirect
from managebook.models import BookLike, Book, BookLike
from django.views import View


class BookView(View):
    def get(self, request):
        response = {}
        response["content"] = Book.objects.prefetch_related("author", "genre", "comment", "comment__user").all()
        return render(request, "index.html", response)

class AddRateBook(View):
    def get(self, request, rate, book_id):
        BookLike.objects.create(book_id=book_id, rate=rate, user_id=request.user.id)
        return redirect("hello")
