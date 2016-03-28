import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "open_airline_manager.settings")

import django
django.setup()

from airline_manager.models import Alliance, Airline, Airport, Hub, Line, Flight, DailyFlight, PlaneType, Plane, Success, Research
import datetime
from django.utils import timezone

now = datetime.datetime.now()
next_day = now.weekday()
day_of_week = (next_day - 1) % 6

airlines = Airline.objects.all()

for airline in airlines:
    income = 0
    # We compute the right price the user should set per km.
    right_first = 0.8 * (airline.security/100. + airline.notoriety/25. + airline.attractiveness/300. - airline.gains / 100. + 1.)
    right_second = 0.2 * (airline.security/200. + airline.notoriety/25. + airline.attractiveness/200. - airline.gains / 200. + 1.)
    right_third = 0.1 * (airline.security/300. + airline.notoriety/25. + airline.attractiveness/100. - airline.gains / 400. + 1.)
    flights = DailyFlight.objects.filter(plane__airline=airline)\
        .select_related('plane', 'plane__type', 'line', 'line__line')
    for flight in flights:
        plane = flight.plane
        line = flight.line
        length = line.line.length
        # We compute occupation of the plane
        pass_first = plane.first * min(max(1.+float(right_first*length-line.price_first)/(right_first*length), 0.), 1)
        pass_second = plane.second * min(max(1.+float(right_second*length-line.price_second)/(right_second*length), 0.), 1)
        pass_third = plane.third * min(max(1.+float(right_third*length-line.price_third)/(right_third*length), 0.), 1)
        # We calculate the profits from this line
        total_passenger = pass_third + pass_second + pass_first
        profit = pass_first * line.price_first + pass_second * line.price_second + pass_third * line.price_third
        profit += total_passenger * airline.gains/50.
        # We calculate the losses
        losses = line.line.start_point.tax + line.line.end_point.tax + plane.type.consumption * length * total_passenger / 100
        airline.money += profit - losses
        income += profit - losses
    # Deleting extra flights
    flights.delete()
    if airline.research_end < timezone.now():
        airline.research.add(airline.research_queue)
        airline.research_queue = None
    # Adding the income and saving all progress
    airline.income_history.pop(0)
    airline.income_history.append(income)
    airline.income = income
    airline.save()

    next_flights = Flight.objects.filter(day=next_day, plane__airline=airline)
    for flight_n in next_flights:
        daily_flight = DailyFlight(line_id=flight_n.line_id, plane_id=flight_n.plane_id, start=flight_n.start)
        daily_flight.save()

# We now compute the rank of all players and update the ranking
airlines.order_by('-income')
rank = 1
for airline in airlines:
    airline.rank_history.pop(0)
    airline.rank_history.append(rank)
    airline.save()
    rank += 1














