from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from airline_manager.forms import AirlineForm
from airline_manager.models import Airline, Airport, PlaneType, Plane, Alliance, Hub, Line, PlayerLine, Flight, \
    DailyFlight, Success
from django.shortcuts import get_object_or_404


def index(request):
    if request.user.is_authenticated():
        return redirect('home')

    return render(request, 'index.html', {})


def register(request):
    if request.user.is_authenticated():
        if not (request.user.airline.exists()):
            active = 2
            if request.method == 'POST':
                form = AirlineForm(request.POST)

                if form.is_valid():
                    airline = form.save(commit=False)
                    airline.owner = request.user
                    airline.save()
                    return redirect('registration-hub')

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
def register_hub(request):
    error = None
    if request.method == 'POST':
        airport_id = request.POST['airport']
        airline = request.user.airline.first()
        airport = Airport.objects.filter(pk=airport_id)
        if airport.exists():
            airport = airport.first()
            if not (Hub.objects.filter(owner=airline, airport=airport).exists()):
                hub = Hub(owner=airline, airport=airport)
                hub.save()
                return redirect('home')
            else:
                error = "Own this hub"

    airports = Airport.objects.all()

    return render(request, 'registration/registration-hub.html', {'airports': airports, 'error': error})


@login_required()
def profile(request):
    airline = request.user.airline.all().select_related('alliance').first()
    return render(request, 'profile.html', {'airline': airline})


@login_required()
def planes_list(request):
    planes = Plane.objects.filter(airline=request.user.airline.first()).select_related('type')
    if planes.exists():
        return render(request, 'plane-list.html', {'planes': planes})
    else:
        # todo. Redirect to the url where the user can buy his first plane
        return redirect('home')


@login_required()
def user_home(request):
    airline = request.user.airline.all().select_related('alliance').first()
    if not Hub.objects.filter(owner=airline).exists():
        return redirect('registration-hub')
    return render(request, 'home.html', {'airline': airline})


@login_required()
def buy_hub(request):
    airports = Airport.objects.all()
    return render(request, 'buy-hub.html', {'airports': airports})


@login_required()
def buy_hub_save(request):
    if request.method == 'POST':
        airportId = request.POST['airport']
        airline = request.user.airline.first()
        if Airport.objects.filter(pk=airportId).exists():
            if not (Hub.objects.filter(owner=airline, airport_id=airportId).exists()):
                hub = Hub()
                hub.owner_id = airline.pk
                hub.airport_id = airportId
                hub.save()
                return redirect('home')
            else:
                airports = Airport.objects.all()
                return render(request, 'buy-hub.html', {'airports': airports, 'error': "Own this hub"})
    else:
        return redirect('buy-hub')


@login_required()
def alliance_home(request):
    alliance_id = request.user.airline.first().alliance_id
    if alliance_id is not None:
        return redirect('alliance', alliance_id=str(alliance_id))
    else:
        alliances = Alliance.objects.all().select_related('founder')
        return render(request, 'alliances.html', {'alliances': alliances})


@login_required()
def alliance(request, alliance_id):
    alliance = get_object_or_404(Alliance, pk=alliance_id)
    airline_list = alliance.members.all()
    return render(request, 'alliance.html', {'airlines': airline_list, 'alliance': alliance})


@login_required()
def test_success(request):
    airline = request.user.airline.all().select_related('alliance').first()
    add_achievement(airline, 2)
    achievement = Success.objects.get(pk=2)
    return render(request, 'home.html', {'airline': airline, 'achievement': achievement})


def add_achievement(airline, achievement_id):
    """Add an achievement to a user

    The function checks that a user doesn't have the achievement yet and then adds it to his profile.

    Args:
        airline: The user we want to reward.
        achievement_id: The achievement we want to add.

    """
    achievement = Success.objects.get(pk=achievement_id)
    if not airline.success.filter(pk=achievement_id):
        airline.success.add(achievement)
