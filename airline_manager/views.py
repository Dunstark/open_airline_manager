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
from django.utils import timezone


def index(request):
    """Index page

    Returns the index page if the user isn't logged in. Otherwise return the homepage.

    Args:
        request: The HTTP request

    Returns: Either the index or the homepage

    """
    if request.user.is_authenticated():
        return redirect('home')

    return render(request, 'index.html', {})


def register(request):
    """Registration Page

    Returns the registration page if the user hasn't completed the registration
    Args:
        request: The HTTP request

    Returns: The correct registration page

    """
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
    """Hub creation page

    Returns the hub registration page

    Args:
        request: The HTTP request

    Returns: The hub registration page

    """
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
    """Profile page

    Returns the user profile page

    Args:
        request: The HTTP request

    Returns:

    """
    airline = request.user.airline.all().select_related('alliance').first()
    return render(request, 'profile.html', {'airline': airline})


@login_required()
def planes_list(request):
    """Planes List

    Returns the list of planes the user owns

    Args:
        request: The HTTP request

    Returns: A list of planes

    """
    planes = Plane.objects.filter(airline=request.user.airline.first()).select_related('type')
    if planes.exists():
        return render(request, 'plane-list.html', {'planes': planes})
    else:
        # todo. Redirect to the url where the user can buy his first plane
        return redirect('home')


@login_required()
def plane_configuration(request, plane_id):
    """Plane Configuration

    Args:
        request: The HTTP request
        plane_id: The id in the DB of the plane you want to change

    Returns: A form to change the configuration

    """
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
    """Plane Planning

    Args:
        request: The HTTP request
        plane_id: The id in the DB of the plane you want to change

    Returns:

    """
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
    """Homepage

    Returns stats about the current user

    Args:
        request: The HTTP request

    Returns: The user homepage

    """
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
    """Buy a hub

    Shows a lis tof hub the user can buy

    Args:
        request: the HTTP request

    Returns:

    """
    airline = request.user.airline.first()
    hubs = airline.hubs.all().values_list('airport_id', flat=True)
    airports = Airport.objects.all().exclude(id__in=hubs)
    return render(request, 'buy-hub.html', {'airports': airports})


@login_required()
def buy_hub_save(request):
    """Buy a hub

    Buy a given hub if possible

    Args:
        request: the HTTP request

    Returns:

    """
    if request.method == 'POST':
        airport_id = request.POST['airport']
        airline = request.user.airline.first()
        airport = Airport.objects.filter(pk=airport_id)
        error = None
        if airport.exists():
            airport = airport.first()
            if not (Hub.objects.filter(owner=airline, airport_id=airport_id).exists()):
                if airline.money < airport.price:
                    hub = Hub()
                    hub.owner_id = airline.pk
                    hub.airport_id = airport_id
                    hub.save()
                    return redirect('home')
                else:
                    error = _("You do not have the necessary funds")
            else:
                error = _("You already own this hub")
            hubs = airline.hubs.all().values_list('airport_id', flat=True)
            airports = Airport.objects.all().exclude(id__in=hubs)
            return render(request, 'buy-hub.html', {'airports': airports, 'error': error})
    else:
        return redirect('buy-hub')


@login_required()
def alliance_home(request):
    """Alliance List

    Shows a list of existing alliance

    Args:
        request: the HTTP request

    Returns:

    """
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
    """Alliance Page

    Shows the alliance information, including a list of users.

    Args:
        request: the HTTP request
        alliance_id: the ID of the alliance the user wants to view

    Returns:

    """
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
    """Make a request to join an alliance

    Args:
        request: the HTTP request
        alliance_id: The alliance the user wants to join

    Returns:

    """
    alli = get_object_or_404(Alliance, pk=alliance_id)
    airline = request.user.airline.first()
    if not AllianceRequest.objects.filter(airline=airline).exists():
        req = AllianceRequest(alliance=alli, airline=airline)
        req.save()
    return redirect('alliance-home')


@login_required()
def allow_into_alliance(request):
    """Allow a player into your alliance

    Args:
        request: the HTTP request

    Returns:

    """
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
    """Research page

    Shows all the research. Allow to do new research

    Args:
        request: the HTTP request

    Returns:

    """
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
    """Leaderboard

    Shows the rank of all the players

    Args:
        request: the HTTP request

    Returns:

    """
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

@login_required()
def buy_plane(request):
    """Plane Buying Process

    Offers a choice of hub to store the plane in

    Args:
        request: the HTTP request

    Returns:

    """
    hubs = Hub.objects.filter(owner=request.user.airline.first())
    return render(request, 'buy-plane-hublist.html', {'hubs': hubs})

@login_required()
def buy_plane_after_hub(request):
    """Choice of a plane type

    Args:
        request: the HTTP request

    Returns:

    """
    if request.method == 'POST':
        # We check the request is legit
        hub_id = request.POST['hub_id']
        hub = Hub.objects.filter(pk=hub_id)
        if hub.exists():
            planetypes = PlaneType.objects.all()
            return render(request, 'buy-plane-typelist.html', {'planetypes': planetypes, 'hub_id': hub_id})

    return redirect('buy-plane')

@login_required()
def buy_plane_save(request):
    """Creation of the planes

    Args:
        request: the HTTP request

    Returns:

    """
    error = None
    airline = request.user.airline.first()
    if request.method == 'POST':
        hub_id = request.POST['hub_id']
        type_id = request.POST['planetype_id']
        quantity = int(request.POST['quantity'])
        hub = Hub.objects.filter(pk=hub_id, owner=airline)
        type = PlaneType.objects.filter(pk=type_id)
        # We check everything is fine with the request
        if hub.exists():
            if type.exists():
                type = type.first()
                hub = hub.first()
                # We check the user has the funds
                if int(quantity * type.price) < airline.money:
                    airline.credit(int(quantity * type.price))
                    # We create the planes
                    for i in range(0,quantity):
                        plane = Plane()
                        plane.name = str(i)
                        plane.type = type
                        plane.airline = airline
                        plane.hub_id = int(hub_id)
                        plane.first = 0
                        plane.second = 0
                        plane.third = type.max_seats
                        plane.available_on = timezone.now()
                        plane.save()
                    return redirect('home')

                else:
                    error = "You don't have enough money "
            else:
                error = "Plane type doesn't exist,please choose another type"
        else:
            error = "Hub doesn't exist, please choose another hub"
    return redirect('buy-plane')


@login_required()
def hub_list(request):
    """Display a list of hubs the user owns

    Args:
        request: the HTTP request

    Returns:

    """
    airline = request.user.airline.first()
    hubs = Hub.objects.filter(owner=airline)
    return render(request, 'hub-list.html',{'hubs': hubs})

@login_required()
def playerline(request, hub_id):
    """Player Lines in a given hub

    Args:
        request: the HTTP request
        hub_id: The hub the user wants to know more about

    Returns:

    """
    airport=Hub.objects.get(pk=hub_id).airport #hubs belong to this user
    airline=request.user.airline.first()
    playerlines=PlayerLine.objects.filter(airline=airline,line__start_point=airport)
    return render(request,'playerline.html',{'playerlines':playerlines})

@login_required()
def buy_line(request, hub_id):
    """Buy a new line

    Args:
        request: the HTTP request
        hub_id: The hub where the user wants the plane to take off.

    Returns:

    """
    error = None
    airline=request.user.airline.first()
    if request.method == 'POST':
        line_id=request.POST['line']
        # Verifying the line doesn't exist.
        if not(PlayerLine.objects.filter(airline=airline, line_id=line_id).exists()):
            playerline=PlayerLine(airline_id=airline.pk, line_id=line_id, price_first=0, price_second=0,price_third=0)
            playerline.save()
            return redirect('home')
        else:
            error = _('You already own this line, please choose another one.')

    airport=Hub.objects.get(pk=hub_id).airport #hub belong to this user
    playerlines=PlayerLine.objects.filter(airline=airline,line__start_point=airport)#lines which client already buy
    lines=Line.objects.filter(start_point=airport).exclude(id__in=playerlines.values_list('line_id')) #lines belong to this airport
    return render(request,'buy-line.html', {'hub_id':hub_id,'error':error,'lines':lines})

@login_required()
def create_alliance(request):
    """Alliance creation process

    Args:
        request: the HTTP request

    Returns:

    """
    error = None
    airline =request.user.airline.first()
    if airline.alliance is None:
        if request.method == 'POST':
            form = AllianceForm(request.POST)

            if form.is_valid():
                alliance=form.save(commit=False)
                alliance.founder_id=airline.pk
                alliance.save()
                airline.alliance = alliance
                airline.save()
                return redirect('home')
        else:
            form=AllianceForm()

        return render(request,'alliance-creation.html',{'form':form})

    return redirect('home')


@login_required()
def marketing(request):
    airline = request.user.airline.first()
    now = timezone.now()
    if (now - airline.last_marketing).days < 7:
        return render(request, 'marketing-no.html')
    else:
        return render(request, 'marketing.html')

@login_required()
def launch_marketing(request):
    if request.method == "POST":
        airline = request.user.airline.first()
        if airline.money > 500000:
            airline.credit(500000)
            airline.last_marketing = timezone.now()
            airline.save()
    return redirect('home')
