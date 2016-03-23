from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from airline_manager.forms import AirlineForm
from airline_manager.models import Airline, Airport, PlaneType, Plane,Hub
from django.utils import timezone

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
def hubs_list(request):
    hubs=request.user.airline.first().hubs.all().select_related('airport')
    return render(request,'hub-list.html',{'hubs':hubs})


@login_required()
def hub(request):
    airport=Airport.objects.all()
    return render(request, 'buy-hub-list.html', {'airports':airport})

@login_required()
def buy_hub(request):
    if request.method == 'POST':   #当提交表单时
        airportId=request.POST['airport_id']
        airline = request.user.airline.first()  #request是什么,上面那个hub为啥不用request
        if Airport.objects.filter(pk=airportId).exists():
            if not(Hub.objects.filter(owner=airline, airport_id = airportId).exists()):
                hub=Hub()
                hub.owner_id = airline.pk
                hub.airport_id = airportId
                hub.save()
                return redirect('home')
            else:
                return render(request, 'buy-hub.html', {})

@login_required()
def buy_plane(request):
    hubs = Hub.objects.filter(owner=request.user.airline.first())
    return render(request, 'buy-plane-hublist.html', {'hubs': hubs})

@login_required()
def buy_plane_after_hub(request):
    if request.method == 'POST':
        hub_id = request.POST['hub_id']
        hub = Hub.objects.filter(pk=hub_id)
        if (hub.exists()) :
            planetypes = PlaneType.objects.all()
            return render(request, 'buy-plane-typelist.html', {'planetypes': planetypes, 'hub_id': hub_id})

    return redirect('buy-plane')

@login_required()
def buy_plane_save(request):
    error = None
    airline = request.user.airline.first()
    if request.method == 'POST':
        hub_id = request.POST['hub_id']
        type_id = request.POST['planetype_id']
        quantity = int(request.POST['quantity'])
        hub = Hub.objects.filter(pk=hub_id, owner=airline)
        type = PlaneType.objects.filter(pk=type_id)
        if hub.exists():
            if type.exists():
                type = type.first()
                hub = hub.first()
                if int(quantity * type.price) < airline.money:
                    airline.credit(int(quantity * type.price))
                    airline.save()
                    for i in range(0,quantity):
                        plane = Plane()
                        plane.name = str(i)
                        plane.type = type
                        plane.airline = airline
                        plane.first = 0
                        plane.second = 0
                        plane.third = type.max_seats
                        plane.available_on = timezone.now()
                        plane.save()
                    return redirect('home')

                else:
                    error = 'You don\'t have enough money '
            else:
                error = 'Plane type doesn\'t exist,please choose another type'
        else:
            error = 'Hub doesn\'t exist, please choose another hub'
    return redirect('buy-plane')

