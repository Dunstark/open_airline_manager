from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    return render(request, 'template.html', {})


def profile(request):
    return render(request, 'profile.html', {})


def user_home(request):
    return render(request, 'template.html', {})

