from __future__ import unicode_literals

from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User


class Airline(models.Model):
    name = models.CharField(max_length=45, unique=True)
    money = models.BigIntegerField(default=100000000)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="airline")
    alliance = models.ForeignKey("Alliance", null=True, on_delete=models.SET_NULL, related_name="members")

    def __str__(self):
        return self.name

    @property
    def is_founder(self):
        if self.alliance:
            return self.alliance.founder == self
        else:
            return False


class Alliance(models.Model):
    name = models.CharField(max_length=45, unique=True)
    money = models.BigIntegerField(default=0)
    founder = models.OneToOneField(Airline, on_delete=models.CASCADE, related_name="alliance_founder")

    def __str__(self):
        return self.name

    @property
    def member_funds(self):
        return self.members.aggregate(Sum('money'))['money__sum']


class Airport(models.Model):
    name = models.CharField(max_length=90, unique=True)
    city = models.CharField(max_length=90)
    iata = models.CharField(max_length=3, unique=True)

    def __str__(self):
        return self.iata + self.city + " - " + self.name


class Line(models.Model):
    start_point = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="as_start_point")
    end_point = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="as_end_point")
    length = models.IntegerField()

    def __str__(self):
        return self.start_point + " - " + self.end_point


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

    def __str__(self):
        return self.manufacturer + self.name

    def can_fly_line(self, line):
        return self.range >= line.length


class Plane(models.Model):
    name = models.CharField(max_length=8)
    type = models.ForeignKey(PlaneType, on_delete=models.CASCADE)
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE)
    first = models.IntegerField()
    second = models.IntegerField()
    third = models.IntegerField()

    def __str__(self):
        return self.type + " - " + self.name

    def is_valid_configuration(self, first_p, second_p, third_p):
        if ((third_p + 2*second_p + 4 * first_p) <= self.type.max_seats) and third_p >= 0 and second_p >= 0 and first_p >= 0:
            return True
        else:
            return False
