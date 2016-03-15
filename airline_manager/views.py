from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from airline_manager.forms import AirlineForm
from airline_manager.models import Airline, Airport, PlaneType, Plane,Hub,Alliance
from django.shortcuts import get_object_or_404

def index(request):
    if request.user.is_authenticated():
        return redirect('home')

    return render(request, 'index.html', {})

def register(request):
    if request.user.is_authenticated():
        if not(request.user.airline.exists()):
            active = 2
            if request.method == 'POST':
                form = AirlineForm(request.POST)

                if form.is_valid():
                    airline = form.save(commit=False)
                    airline.owner = request.user
                    airline.save()
                    return redirect('home')

            else:
                form = AirlineForm()

        else:
            return redirect('home')
    else:
        active = 1
        if request.method == 'POST':
            form = UserCreationForm(request.POST)

            if form.is_valid():
                form.save()
                new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'],
                                    )
                login(request, new_user)
                return redirect('registration')

        else:
            form = UserCreationForm()

    return render(request, 'registration/registration.html', {'form': form, 'active': active})

@login_required()
def profile(request):
    return render(request, 'profile.html', {})

@login_required()
def planes_list(request):
    planes = Plane.objects.filter(airline=request.user.airline.first()).select_related('type')
    return render(request, 'plane-list.html', {'planes': planes})


@login_required()
def user_home(request):
    airline = request.user.airline.all().select_related('alliance').first()
    return render(request, 'home.html', {'airline': airline})

@login_required()
def buy_hub(request):
    airport=Airport.objects.all()
    return render(request, 'buy-hub.html', {'airports':airport})

@login_required()
def buy_hub_save(request):
    if request.method == 'POST':
        airportId=request.POST['airport']
        airline = request.user.airline.first()
        if Airport.objects.filter(pk=airportId).exists():
            if not(Hub.objects.filter(owner=airline, airport_id = airportId).exists()):
                hub=Hub()
                hub.owner_id = airline.pk
                hub.airport_id = airportId
                hub.save()
                return redirect('home')
            else:
                airport=Airport.objects.all()
                return render(request, 'buy-hub.html', {'airports':airport, 'error': "Own this hub"})

@login_required()
def alliance(request,alliance_id):
    alliance=get_object_or_404(Alliance,pk=alliance_id)
    airline_list=alliance.members.all()
    return render(request, 'alliance.html', {'airlines':airline_list, 'alliance':alliance})

