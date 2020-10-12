from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, widgets, Textarea, TextInput, SelectMultiple
from django import forms
from managebook.models import Book, Comment


class BookForm(ModelForm):
    class Meta:
        model = Book
        fields = ('title', 'text', 'genre')
        widgets = {
            "title": TextInput(attrs={"class": "form-control"}),
            "text": Textarea(attrs={"class": "form-control", "rows": 3, "cols": 4}),
            "genre": SelectMultiple(attrs={"class": "form-control"})
        }
        labels = {
            "title": "hello title"
        }
        help_texts = {
            "text": "enter youre text here"
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ("text",) #Tuple or list?
        widgets = {
            "text": Textarea(attrs={"class": "form-control", "rows": 3})
        }


class CustomUserCreateForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        widgets = {'username': TextInput(attrs={"class": "form-control"})}
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', "class": "form-control"}),

    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', "class": "form-control"}),
        strip=False,

    )
