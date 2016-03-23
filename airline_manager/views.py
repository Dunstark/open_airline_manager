import math
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from airline_manager.forms import AirlineForm, ConfigurationForm, LineChoiceForm
from airline_manager.models import Airline, Airport, PlaneType, Plane, Alliance, Hub, Line, PlayerLine, Flight, \
    DailyFlight, Success, AllianceRequest, Research, News
from django.shortcuts import get_object_or_404
import datetime
from django.utils.translation import ugettext as _


def index(request):
    if request.user.is_authenticated():
        return redirect('home')

    return render(request, 'index.html', {})


def register(request):
    if request.user.is_authenticated():
        if not (request.user.airline.all().exists()):
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
def plane_configuration(request, plane_id):
    plane = get_object_or_404(Plane, pk=plane_id)
    if request.method == 'POST':
        form = ConfigurationForm(request.POST, instance=plane)
        if form.is_valid():
            form.save()
            return redirect('planes')
    else:
        form = ConfigurationForm(instance=plane)

    return render(request, 'plane-configuration.html', {'form': form, 'plane_id': plane_id})


@login_required()
def plane_planning(request, plane_id):
    plane = get_object_or_404(Plane, pk=plane_id)
    airline = request.user.airline.first()
    airport = plane.hub.airport
    initial = {'airline': airline, 'airport': airport}
    if request.method == 'POST':
        form = LineChoiceForm(request.POST, initial=initial)
        if form.is_valid():
            # Getting the new player line
            line = form.cleaned_data['line']
            if plane.airline == airline and line.airline == airline:
                # Deleting existing flights for this plane
                Flight.objects.filter(plane=plane).delete()

                time = 0
                day = 0
                day_next = 0

                flight_time = math.ceil(2 * line.line.length / plane.type.speed) * 30
                while day < 7:
                    time_next = (time + flight_time) % (24 * 30 * 2)
                    day_next += ((time + flight_time)/(24 * 30 * 2))
                    if day_next < 7:
                        flight = Flight()
                        flight.day = int(day)
                        flight.start = datetime.time(hour=int(time/60), minute=int(time % 60))
                        flight.plane = plane
                        flight.line = line
                        flight.save()
                    time = time_next
                    day = day_next
                return redirect('planes')
            else:
                form.add_error('', _('You do not own this line'))

    else:
        form = LineChoiceForm(initial=initial)

    return render(request, 'plane-planning.html', {'form': form, 'plane_id': plane_id})


@login_required()
def user_home(request):
    airline = request.user.airline.all().select_related('alliance').first()
    if not Hub.objects.filter(owner=airline).exists():
        return redirect('registration-hub')
    flights = Flight.objects.filter(line__airline=airline).select_related('line__line', 'plane')[:10]
    try:
        news = News.objects.all().latest('date')
    except News.DoesNotExist:
        news = None
    return render(request, 'home.html', {'airline': airline, 'flights': flights, 'news': news})


@login_required()
def buy_hub(request):
    airline = request.user.airline.first()
    hubs = airline.hubs.all().values_list('airport_id', flat=True)
    airports = Airport.objects.all().exclude(id__in=hubs)
    return render(request, 'buy-hub.html', {'airports': airports})


@login_required()
def buy_hub_save(request):
    if request.method == 'POST':
        airport_id = request.POST['airport']
        airline = request.user.airline.first()
        if Airport.objects.filter(pk=airport_id).exists():
            if not (Hub.objects.filter(owner=airline, airport_id=airport_id).exists()):
                hub = Hub()
                hub.owner_id = airline.pk
                hub.airport_id = airport_id
                hub.save()
                return redirect('home')
            else:
                hubs = airline.hubs.all().values_list('airport_id', flat=True)
                airports = Airport.objects.all().exclude(id__in=hubs)
                return render(request, 'buy-hub.html', {'airports': airports, 'error': "Own this hub"})
    else:
        return redirect('buy-hub')


@login_required()
def alliance_home(request):
    airline = request.user.airline.first()
    alliance_id = airline.alliance_id
    if alliance_id is not None:
        return redirect('alliance', alliance_id=str(alliance_id))
    else:
        alliances = Alliance.objects.all().select_related('founder')
        requests = AllianceRequest.objects.filter(airline=airline)
        return render(request, 'alliances.html', {'alliances': alliances, 'requests': requests})


@login_required()
def alliance_view(request, alliance_id):
    alliance = get_object_or_404(Alliance, pk=alliance_id)
    airline_list = alliance.members.all()
    airline = request.user.airline.first()
    requests = None
    is_founder = airline.is_founder
    if is_founder:
        requests = alliance.join_requests.all().select_related('airline')
    return render(request, 'alliance.html',
                  {'airlines': airline_list, 'alliance': alliance, 'is_founder': is_founder, 'requests': requests})


@login_required()
def alliance_join(request, alliance_id):
    alli = get_object_or_404(Alliance, pk=alliance_id)
    airline = request.user.airline.first()
    if not AllianceRequest.objects.filter(alliance=alli, airline=airline).exists():
        req = AllianceRequest(alliance=alli, airline=airline)
        req.save()
    return redirect('alliance-home')


@login_required()
def allow_into_alliance(request):
    if request.method == 'POST':
        airline = request.user.airline.select_related('alliance').first()
        alliance = airline.alliance
        if airline.is_founder:
            req = get_object_or_404(AllianceRequest, pk=request.POST.get('req_id', None))
            if req.alliance == alliance:
                req.airline.alliance = alliance
                req.airline.save()
                req.delete()

    return redirect('alliance-home')

@login_required()
def research_list(request):
    airline = request.user.airline.select_related('alliance').first()
    if request.method == 'POST':
        research = Research.objects.get(pk=request.POST['research'])
        if not airline.research.filter(pk=request.POST['research']).exists():
            airline.research_queue = research
            airline.research_end = datetime.datetime.now() + datetime.timedelta(hours=3)
            airline.save()
    research_done = airline.research.all()
    research_list = Research.objects.all().exclude(id__in=research_done.values_list('id', flat=True))

    return render(request, 'research.html', {'research_done': research_done, 'research_list': research_list,
                                             'current_research': airline.research_queue, 'airline': airline})


@login_required()
def airline_leaderboard(request):
    airlines = Airline.objects.all().exclude(rank=0).order_by('rank')[:10]
    return render(request, 'ranking.html', {'airlines': airlines})


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
