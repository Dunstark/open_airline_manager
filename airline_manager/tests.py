from django.test import TestCase
from django.contrib.auth.models import User
from airline_manager.models import Airline, Alliance, Airport, PlaneType, Line, Plane, Hub


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
        self.a1 = Airline.objects.create(name="Airline 1", owner=User.objects.create(username="o1"), money=2)
        self.airport1 = Airport.objects.create(name="Airport 1", iata="A11", city="City 1")
        self.airport2 = Airport.objects.create(name="Airport 2", iata="A21", city="City 1")
        self.hub1 = Hub.objects.create(airport=self.airport1, owner=self.a1)
        self.line1 = Line.objects.create(start_point=self.airport1, end_point=self.airport2, length=100)
        self.line2 = Line.objects.create(start_point=self.airport1, end_point=self.airport2, length=350)
        self.planeModel1 = PlaneType.objects.create(name="A380", manufacturer=0, range=200, max_seats=200, price=20000)
        self.plane1 = Plane.objects.create(name="AF547", type=self.planeModel1, airline=self.a1, first=0, second=0, third=200, hub=self.hub1)

    def test_length(self):
        """Planes are allowed to fly the correct lines"""
        self.assertTrue(self.planeModel1.can_fly_line(self.line1))
        self.assertFalse(self.planeModel1.can_fly_line(self.line2))

    def test_config(self):
        """Plane configuration is correctly validated"""
        self.assertTrue(self.plane1.is_valid_configuration(10, 25, 110))
        self.assertFalse(self.plane1.is_valid_configuration(200, 25, 110))


class HomeViewTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username="o1", password="testuser")
        self.a1 = Airline.objects.create(name="Airline 1", owner=self.user1, money=2)
        self.airport1 = Airport.objects.create(name="Airport 2", iata="A21", city="City 1")
        self.hub1 = Hub.objects.create(airport=self.airport1, owner=self.a1)


    def test_page_redirects(self):
        """Home page correctly redirects a user that isn't logged to the homepage"""
        response = self.client.get('/home/')
        self.assertEquals(response.status_code, 302)

    def test_page_loads(self):
        """Home page loads correctly when the user is logged in"""
        self.client.login(username="o1", password="testuser")
        response = self.client.get('/home/')
        self.assertEquals(response.status_code, 200)


class IndexViewTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username="o1", password="testuser")

    def test_page_redirects(self):
        """Index page redirects correctly when the user is logged in"""
        self.client.login(username="o1", password="testuser")
        response = self.client.get('/')
        self.assertEquals(response.status_code, 302)

    def test_page_loads(self):
        """Index page loads correctly when the user isn' logged in"""
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)



class RegistrationViewTestCase(TestCase):

    def test_page_loads(self):
        """Register page loads"""
        response = self.client.get('/register/')
        self.assertEquals(response.status_code, 200)


class ProfileViewTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username="o1", password="testuser")

    def test_page_redirects(self):
        """Profile page correctly redirects a user that isn't logged to the homepage"""
        response = self.client.get('/profile/')
        self.assertEquals(response.status_code, 302)

    def test_page_loads(self):
        """Profile page loads correctly when the user is logged in"""
        self.client.login(username="o1", password="testuser")
        response = self.client.get('/profile/')
        self.assertEquals(response.status_code, 200)


