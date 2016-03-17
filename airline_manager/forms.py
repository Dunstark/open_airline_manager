from django.forms import ModelForm
from django.core.exceptions import NON_FIELD_ERRORS
from airline_manager.models import Airline, PlaneType, Plane

class AirlineForm(ModelForm):
    class Meta:
        model = Airline
        fields = ['name']


class ConfigurationForm(ModelForm):
    class Meta:
        model = Plane
        fields = ['first', 'second', 'third']