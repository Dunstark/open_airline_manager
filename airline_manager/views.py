from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

# Create your views here.

def index(request):
    return render(request, 'index.html', {})

def register(request):
    if request.user.is_authenticated():
        return redirect('home')
    else:
        if request.method == 'POST':
            form = UserCreationForm(request.POST)

            if form.is_valid():
                form.save()
                new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'],
                                    )
                login(request, new_user)
                return redirect('home')

        else:
            form = UserCreationForm()

        return render(request, 'registration/registration.html', {'form': form})


@login_required()
def profile(request):
    return render(request, 'profile.html', {})

@login_required()
def user_home(request):
    return render(request, 'home.html', {})

