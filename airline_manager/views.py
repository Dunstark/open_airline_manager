from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Create your views here.

def index(request):
    return render(request, 'template.html', {})

@login_required()
def profile(request):
    return render(request, 'profile.html', {})

@login_required()
def user_home(request):
    return render(request, 'template.html', {})

