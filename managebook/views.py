from django.http import HttpResponse
from django.shortcuts import render


# def hello(request):
#     return HttpResponse("Hello world")

def hello(request):
    response = {"user": "oleg", "digit": 54}
    return render(request, 'index.html', response)
