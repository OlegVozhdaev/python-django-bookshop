from django.contrib import admin

from managebook.models import Book, Genre, Comment


class CommentAdmin(admin.StackedInline):
    model = Comment
    extra = 2
    readonly_fields = ["like"]


class BookAdmin(admin.ModelAdmin):
    inlines = [CommentAdmin]
    prepopulated_fields = {"slug": ("title",)}
    list_display = ["title", "publish_date"]
    search_fields = ["title"]
    list_filter = ["publish_date", "author", "genre"]


# Register your models here.
admin.site.register(Book, BookAdmin)
admin.site.register(Genre)
