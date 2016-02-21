from django.test import TestCase
from django.contrib.auth.models import User
from airline_manager.models import Airline, Alliance, Airport, PlaneType, Line


class AllianceTestCase(TestCase):
    def setUp(self):
        self.a1 = Airline.objects.create(name="Airline 1", owner=User.objects.create(username="o1"), money=2)
        self.a2 = Airline.objects.create(name="Airline 2", owner=User.objects.create(username="o2"), money=3)
        self.a3 = Airline.objects.create(name="Airline 3", owner=User.objects.create(username="o3"), money=7)
        self.alliance1 = Alliance.objects.create(name="TEST Alliance", founder=self.a1, money=11)
        self.a1.alliance = self.alliance1
        self.a1.save()
        self.a2.alliance = self.alliance1
        self.a2.save()

    def test_correct_owner(self):
        """Owner is properly identified"""
        self.assertTrue(self.a1.is_founder)
        self.assertFalse(self.a2.is_founder)
        self.assertFalse(self.a3.is_founder)

    def test_member_funds(self):
        """Alliance members funds is correctly calculated"""
        self.assertEqual(self.alliance1.member_funds, 5)


class PlaneTestCase(TestCase):
    def setUp(self):
        self.airport1 = Airport.objects.create(name="Airport 1", iata="A11", city="City 1")
        self.airport2 = Airport.objects.create(name="Airport 2", iata="A21", city="City 1")
        self.line1 = Line.objects.create(start_point=self.airport1, end_point=self.airport2, length=100)
        self.line2 = Line.objects.create(start_point=self.airport1, end_point=self.airport2, length=350)
        self.plane1 = PlaneType.objects.create(name="A380", manufacturer=0, range=200, max_seats=200)

    def test_length(self):
        """Planes are allowed to fly the correct lines"""
        self.assertTrue(self.plane1.can_fly_line(self.line1))
        self.assertFalse(self.plane1.can_fly_line(self.line2))