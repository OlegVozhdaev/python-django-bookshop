from django.urls import path

from managebook import views

urlpatterns = [
    path("hello/", views.BookView.as_view(), name="hello"),
    path("add_rate/<int:rate>/<int:book_id>>", views.AddRateBook.as_view(), name="add_rate")
]

