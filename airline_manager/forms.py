from django.forms import ModelForm, Form, ModelChoiceField
from django.core.exceptions import NON_FIELD_ERRORS
from airline_manager.models import Airline, Alliance,PlaneType, Plane, Hub, Airport, Line, PlayerLine
from django.utils.translation import ugettext as _
import sys


class AirlineForm(ModelForm):
    class Meta:
        model = Airline
        fields = ['name']


class ConfigurationForm(ModelForm):
    class Meta:
        model = Plane
        fields = ['first', 'second', 'third']

    def is_valid(self):
        # Running the ModelForm default validation
        valid = super(ModelForm, self).is_valid()

        # we're done now if not valid
        if not valid:
            return valid

        if self.instance.is_valid_configuration(self.cleaned_data['first'], self.cleaned_data['second'],
                                                self.cleaned_data['third']):
            return True
        else:
            self.add_error(None, _("You have selected too many seats"))
            return False


class LineChoiceForm(Form):

    def __init__(self, *args, **kwargs):
        super(LineChoiceForm, self).__init__(*args, **kwargs)
        possible_lines = self.initial['airline'].lines.filter(line__start_point_id=self.initial['airport'])
        self.fields['line'] = ModelChoiceField(queryset=possible_lines)

class AllianceForm(ModelForm):
    class Meta:
        model = Alliance
        fields = ['name']
