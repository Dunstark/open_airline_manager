from __future__ import unicode_literals

from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from django.utils.functional import cached_property
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
import datetime


class Success(models.Model):
    name = models.CharField(max_length=90)
    desc = models.CharField(max_length=255)
    points = models.IntegerField()

    def __str__(self):
        return self.name


class Airline(models.Model):
    name = models.CharField(max_length=45, unique=True)
    money = models.BigIntegerField(default=100000000)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="airline")
    alliance = models.ForeignKey("Alliance", blank=True, null=True, on_delete=models.SET_NULL, related_name="members")
    raw_notoriety = models.IntegerField(default=0)
    last_marketing = models.DateTimeField(default=timezone.now, blank=True, null=True)
    last_updated = models.DateTimeField(default=timezone.now)
    research = models.ManyToManyField("Research", blank=True, related_name="airlines")
    research_queue = models.ForeignKey("Research", null=True, related_name="airlines_currently_researching")
    research_end = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    success = models.ManyToManyField(Success, blank=True)
    rank_history = ArrayField(models.BigIntegerField(), size=7)
    income_history = ArrayField(models.BigIntegerField(), size=7)

    def __str__(self):
        return self.name

    @property
    def rank(self):
        return self.rank_history[0]

    @property
    def is_founder(self):
        if self.alliance:
            return self.alliance.founder == self
        else:
            return False

    @cached_property
    def notoriety(self):
        return self.raw_notoriety

    @cached_property
    def attractiveness(self):
        return self.research.aggregate(total=Sum('attractiveness'))['total']

    @cached_property
    def effectiveness(self):
        return self.research.aggregate(total=Sum('effectiveness'))['total']

    @cached_property
    def security(self):
        return self.research.aggregate(total=Sum('security'))['total']

    @cached_property
    def gains(self):
        return self.research.aggregate(total=Sum('gains'))['total']

    @cached_property
    def score(self):
        return self.success.aggregate(total=Sum('points'))['total']

    @cached_property
    def number_of_success(self):
        return self.success.count(), Success.objects.count()

    def debit(self, amount):
        self.money += amount

    def credit(self, amount):
        self.money -= amount


class Alliance(models.Model):
    name = models.CharField(max_length=45, unique=True)
    money = models.BigIntegerField(default=0)
    founder = models.OneToOneField(Airline, on_delete=models.CASCADE, related_name="alliance_founder")
    rank = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    @property
    def member_funds(self):
        return self.members.aggregate(Sum('money'))['money__sum']


class Loan(models.Model):
    borrower = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name="loans")
    amount = models.IntegerField()
    still_to_be_paid = models.FloatField()
    interest_rate = models.FloatField()


class Airport(models.Model):
    name = models.CharField(max_length=90, unique=True)
    city = models.CharField(max_length=90)
    iata = models.CharField(max_length=3, unique=True)
    type = models.IntegerField(default=9)
    tax = models.IntegerField(default=10)

    def __str__(self):
        return self.iata + self.city + " - " + self.name


class Hub(models.Model):
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="hubs")
    owner = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name="hubs")

    def __str__(self):
        return str(self.airport)


class Line(models.Model):
    start_point = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="as_start_point")
    end_point = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="as_end_point")
    length = models.IntegerField()

    def __str__(self):
        return str(self.start_point) + " - " + str(self.end_point)


class PlayerLine(models.Model):
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name="lines")
    line = models.ForeignKey(Line, on_delete=models.CASCADE, related_name="lines_using")
    price_first = models.IntegerField()
    price_second = models.IntegerField()
    price_third = models.IntegerField()


MANUFACTURER_CHOICES = (
    (0, 'Airbus'),
    (1, 'Boeing'),
    (2, 'Bombardier'),
    (3, 'Embraer'),
    (4, 'Tupolev'),
    (5, 'BAE'),
    (6, 'SAAB'),
    (7, 'Sukhoi'),
    (8, 'ATR')
)


class PlaneType(models.Model):
    name = models.CharField(max_length=20,unique=True)
    manufacturer = models.IntegerField(choices=MANUFACTURER_CHOICES)
    range = models.PositiveIntegerField()
    max_seats = models.IntegerField()
    price = models.PositiveIntegerField()
    consumption = models.FloatField(default=4)

    def __str__(self):
        return self.get_manufacturer_display() + " " + self.name

    def can_fly_line(self, line):
        """Indicates if a plane can fly a given line.

        Args:
            line: a Line object we want to test.

        Returns:
            A boolean indicating if the plane can be used on this line.

        """
        return self.range >= line.length


class Plane(models.Model):
    name = models.CharField(max_length=8)
    type = models.ForeignKey(PlaneType, on_delete=models.CASCADE)
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE)
    first = models.IntegerField()
    second = models.IntegerField()
    third = models.IntegerField()
    active = models.IntegerField(default=0)
    available_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.type) + " - " + self.name

    def is_valid_configuration(self, first_p, second_p, third_p):
        """Checks that a new configuration for the plane is possible.

        Args:
            first_p: The number of seats in the first class.
            second_p: The number of seats in the second class.
            third_p: The number of seats in the third class.

        Returns:
            A boolean indicating if the configuration is valid

        """
        if ((third_p + 2*second_p + 4 * first_p) <= self.type.max_seats) and third_p >= 0 and second_p >= 0 and first_p >= 0:
            return True
        else:
            return False


class Flight(models.Model):
    plane = models.ForeignKey(Plane, on_delete=models.CASCADE, related_name="flights")
    line = models.ForeignKey(Line, on_delete=models.CASCADE)
    day = models.IntegerField(default=0)
    start = models.TimeField(default=datetime.datetime.now)


class DailyFlight(models.Model):
    plane = models.ForeignKey(Plane, on_delete=models.CASCADE, related_name="today_flights")
    line = models.ForeignKey(Line, on_delete=models.CASCADE)
    start = models.TimeField(default=datetime.datetime.now)
    accounted_for = models.BooleanField(default=False)


class News(models.Model):
    title = models.CharField(max_length=90)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Research(models.Model):
    title = models.CharField(max_length=90)
    attractiveness = models.IntegerField()
    security = models.IntegerField()
    effectiveness = models.IntegerField()
    gains = models.IntegerField()