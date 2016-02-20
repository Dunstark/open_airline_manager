from django.test import TestCase
from django.contrib.auth.models import User
from airline_manager.models import Airline, Alliance


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
