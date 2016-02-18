from django.forms import ModelForm
from django.core.exceptions import NON_FIELD_ERRORS
from airline_manager.models import Airline

class AirlineForm(ModelForm):
    class Meta:
        model = Airline
        fields = ['name']