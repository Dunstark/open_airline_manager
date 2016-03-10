from __future__ import unicode_literals

from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from django.utils.functional import cached_property


class Airline(models.Model):
    name = models.CharField(max_length=45, unique=True)
    money = models.BigIntegerField(default=100000000)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="airline")
    alliance = models.ForeignKey("Alliance", blank=True, null=True, on_delete=models.SET_NULL, related_name="members")
    raw_notoriety = models.IntegerField(default=0)
    last_marketing = models.DateField(auto_now_add=True, blank=True, null=True)
    research = models.ManyToManyField("Research", blank=True, related_name="airlines")
    research_queue = models.ForeignKey("Research", null=True, related_name="airlines_currently_researching")
    research_end = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    success = models.ManyToManyField("Success", blank=True)
    rank = models.IntegerField(default=0)

    def __str__(self):
        return self.name

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
        return 0

    @cached_property
    def effectiveness(self):
        return 0

    @cached_property
    def security(self):
        return 0

    @cached_property
    def gains(self):
        return 0

    @cached_property
    def score(self):
        return 0

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


class Success(models.Model):
    name = models.CharField(max_length=90)
    desc = models.CharField(max_length=255)
    points = models.IntegerField()

    def __str__(self):
        return self.name


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
    lines = models.ManyToManyField('Line')

    def __str__(self):
        return str(self.airport)


class Line(models.Model):
    start_point = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="as_start_point")
    end_point = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="as_end_point")
    length = models.IntegerField()

    def __str__(self):
        return str(self.start_point) + " - " + str(self.end_point)


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
        if ((third_p + 2*second_p + 4 * first_p) <= self.type.max_seats) and third_p >= 0 and second_p >= 0 and first_p >= 0:
            return True
        else:
            return False


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